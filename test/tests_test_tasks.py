import pytest
from downloader.tasks import process_download
from downloader.models import Download
from unittest.mock import patch
from celery.exceptions import Retry

pytestmark = pytest.mark.django_db

class TestDownloadTasks:
    """Test suite for Celery tasks"""

    def test_process_download_success(self, create_test_download, mock_successful_download):
        """Test successful download processing"""
        download = create_test_download()
        
        with patch('downloader.services.downloader.MediaDownloader.download') as mock_download:
            mock_download.return_value = mock_successful_download
            
            result = process_download.apply(args=[str(download.id), download.url])
            
            assert result.successful()
            download.refresh_from_db()
            assert download.status == Download.Status.COMPLETED

    def test_process_download_retry(self, create_test_download):
        """Test download task retry mechanism"""
        download = create_test_download()
        
        with patch('downloader.services.downloader.MediaDownloader.download') as mock_download:
            mock_download.side_effect = Exception('Network error')
            
            with pytest.raises(Retry):
                process_download.apply(args=[str(download.id), download.url])
            
            download.refresh_from_db()
            assert download.status == Download.Status.FAILED

    def test_process_download_max_retries(self, create_test_download):
        """Test download task max retries behavior"""
        download = create_test_download()
        
        with patch('downloader.services.downloader.MediaDownloader.download') as mock_download:
            mock_download.side_effect = Exception('Permanent error')
            
            # Simulate max retries
            task = process_download.s(str(download.id), download.url)
            task.max_retries = 0
            
            result = task.apply()
            
            assert not result.successful()
            download.refresh_from_db()
            assert download.status == Download.Status.FAILED