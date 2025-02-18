import pytest
from downloader.services.downloader import MediaDownloader
from downloader.services.extractor import MediaExtractor
from downloader.exceptions import DownloadError, MediaNotFoundError
from unittest.mock import patch, Mock
import aiohttp
import asyncio

class TestMediaDownloader:
    """Test suite for MediaDownloader service"""

    @pytest.fixture
    def downloader(self):
        """Create MediaDownloader instance"""
        return MediaDownloader()

    @pytest.mark.asyncio
    async def test_download_success(self, downloader, mock_successful_download):
        """Test successful media download"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.headers = {'content-type': 'image/jpeg'}
            mock_response.content.read = Mock(return_value=b'fake_image_data')
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await downloader.download('https://example.com/image.jpg')
            
            assert result['status'] == 'success'
            assert 'file_path' in result

    @pytest.mark.asyncio
    async def test_download_network_error(self, downloader):
        """Test download with network error"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = aiohttp.ClientError()
            
            with pytest.raises(DownloadError):
                await downloader.download('https://example.com/image.jpg')

class TestMediaExtractor:
    """Test suite for MediaExtractor service"""

    @pytest.fixture
    def extractor(self):
        """Create MediaExtractor instance"""
        return MediaExtractor()

    @pytest.mark.asyncio
    async def test_extract_media_info_success(self, extractor):
        """Test successful media info extraction"""
        with patch('yt_dlp.YoutubeDL') as mock_yt:
            mock_yt.return_value.extract_info.return_value = {
                'url': 'https://example.com/image.jpg',
                'ext': 'jpg',
                'thumbnails': [{'url': 'thumb.jpg'}]
            }
            
            result = await extractor.extract_media_info(
                'https://www.instagram.com/p/valid/'
            )
            
            assert result['urls']
            assert result['type']

    @pytest.mark.asyncio
    async def test_extract_media_info_not_found(self, extractor):
        """Test media extraction when content not found"""
        with patch('yt_dlp.YoutubeDL') as mock_yt:
            mock_yt.return_value.extract_info.side_effect = Exception('Not found')
            
            with pytest.raises(MediaNotFoundError):
                await extractor.extract_media_info(
                    'https://www.instagram.com/p/invalid/'
                )