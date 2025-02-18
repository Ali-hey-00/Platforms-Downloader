import os
import logging
from typing import Dict, Any, Optional
from celery import shared_task
from celery.signals import task_failure, task_success
from django.conf import settings
from datetime import datetime
import aiohttp
import asyncio
from .models import Download
from .services.extractor import MediaExtractor
from .exceptions import DownloadError, MediaNotFoundError
from .utils.file_handlers import sanitize_filename, ensure_unique_filename
from .utils.validators import validate_mime_type

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    rate_limit='10/m',
    queue='downloads'
)
def process_download(
    self,
    download_id: str,
    url: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process media download in background
    
    Args:
        download_id: UUID of the Download instance
        url: Instagram media URL
        options: Additional download options
    
    Returns:
        Dict containing download results
    """
    logger.info(f"Starting download task for {url}", extra={'download_id': download_id})
    
    try:
        # Get or create download instance
        download = Download.objects.get(id=download_id)
        download.status = 'DOWNLOADING'
        download.save()

        # Initialize media extractor
        extractor = MediaExtractor()
        
        # Extract media information
        loop = asyncio.get_event_loop()
        media_info = loop.run_until_complete(extractor.extract_media_info(url))
        
        if not media_info:
            raise MediaNotFoundError(f"No media found at {url}")
        
        # Process each media URL
        results = []
        for media_url in media_info['urls']:
            result = download_media(
                media_url,
                download,
                mime_type=media_info.get('type'),
                options=options
            )
            results.append(result)
        
        # Update download status
        download.status = 'COMPLETED'
        download.completed_at = datetime.utcnow()
        download.save()
        
        return {
            'status': 'success',
            'download_id': str(download.id),
            'results': results
        }
        
    except Exception as exc:
        logger.error(
            f"Download failed for {url}",
            exc_info=True,
            extra={'download_id': download_id}
        )
        
        if download:
            download.status = 'FAILED'
            download.error_message = str(exc)
            download.save()
        
        # Retry for specific exceptions
        if isinstance(exc, (aiohttp.ClientError, asyncio.TimeoutError)):
            raise self.retry(exc=exc)
            
        raise DownloadError(f"Download failed: {str(exc)}", url=url)

def download_media(
    url: str,
    download: Download,
    mime_type: str = None,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Download single media file
    
    Args:
        url: Media URL
        download: Download instance
        mime_type: Expected MIME type
        options: Download options
    
    Returns:
        Dict containing download result
    """
    async def _download():
        timeout = aiohttp.ClientTimeout(
            total=settings.DOWNLOAD_TIMEOUT,
            connect=10
        )
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise DownloadError(
                        f"Failed to download media: HTTP {response.status}"
                    )
                
                # Validate content type
                content_type = response.headers.get('content-type', '')
                if not validate_mime_type(content_type):
                    raise DownloadError(
                        f"Unsupported media type: {content_type}"
                    )
                
                # Generate safe filename
                filename = sanitize_filename(
                    os.path.basename(url.split('?')[0])
                )
                filename = ensure_unique_filename(
                    os.path.join(settings.MEDIA_ROOT, 'downloads'),
                    filename
                )
                
                # Download file in chunks
                file_size = 0
                file_path = os.path.join(settings.MEDIA_ROOT, 'downloads', filename)
                
                with open(file_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(
                        settings.DOWNLOAD_CHUNK_SIZE
                    ):
                        if file_size + len(chunk) > settings.MAX_FILE_SIZE:
                            raise DownloadError("File too large")
                        f.write(chunk)
                        file_size += len(chunk)
                
                return {
                    'file_path': file_path,
                    'file_size': file_size,
                    'mime_type': content_type
                }
    
    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(_download())
        
        # Update download instance
        download.file_path = result['file_path']
        download.file_size = result['file_size']
        download.mime_type = result['mime_type']
        download.save()
        
        return {
            'status': 'success',
            'file_path': result['file_path'],
            'file_size': result['file_size'],
            'mime_type': result['mime_type']
        }
        
    except Exception as exc:
        logger.error(f"Media download failed: {str(exc)}", exc_info=True)
        raise

@task_success.connect(sender=process_download)
def handle_successful_download(sender=None, **kwargs):
    """Handle successful download completion"""
    logger.info(
        "Download completed successfully",
        extra={'task_id': kwargs.get('task_id')}
    )

@task_failure.connect(sender=process_download)
def handle_failed_download(sender=None, task_id=None, exception=None, **kwargs):
    """Handle download task failure"""
    logger.error(
        f"Download task failed: {str(exception)}",
        extra={'task_id': task_id},
        exc_info=exception
    )