import pytest
from rest_framework import status
from django.urls import reverse
from downloader.models import Download
from unittest.mock import patch
import json

pytestmark = pytest.mark.django_db

class TestDownloadAPI:
    """Test suite for Download API endpoints"""

    @pytest.fixture
    def download_url(self):
        """Get download API endpoint URL"""
        return reverse('api:download-create')

    def test_create_download_success(self, api_client, download_url, mock_successful_download):
        """Test successful download creation"""
        with patch('downloader.services.downloader.MediaDownloader.download') as mock_download:
            mock_download.return_value = mock_successful_download
            
            response = api_client.post(
                download_url,
                {'url': 'https://www.instagram.com/p/valid/'},
                format='json'
            )
            
            assert response.status_code == status.HTTP_202_ACCEPTED
            assert 'id' in response.data
            assert Download.objects.count() == 1

    def test_create_download_invalid_url(self, api_client, download_url):
        """Test download creation with invalid URL"""
        response = api_client.post(
            download_url,
            {'url': 'https://example.com/invalid'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'url' in response.data['error']['details']

    @pytest.mark.parametrize('url,expected_status', [
        ('https://www.instagram.com/p/valid/', status.HTTP_202_ACCEPTED),
        ('invalid_url', status.HTTP_400_BAD_REQUEST),
        ('', status.HTTP_400_BAD_REQUEST),
    ])
    def test_download_validation(self, api_client, download_url, url, expected_status):
        """Test download endpoint with various inputs"""
        response = api_client.post(
            download_url,
            {'url': url},
            format='json'
        )
        assert response.status_code == expected_status

    def test_download_status_check(self, api_client, create_test_download):
        """Test download status retrieval"""
        download = create_test_download()
        status_url = reverse('api:download-detail', kwargs={'pk': download.pk})
        
        response = api_client.get(status_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == Download.Status.PENDING

    def test_rate_limiting(self, api_client, download_url):
        """Test API rate limiting"""
        with patch('downloader.services.downloader.MediaDownloader.download'):
            # Make multiple requests
            for _ in range(60):
                api_client.post(
                    download_url,
                    {'url': 'https://www.instagram.com/p/valid/'},
                    format='json'
                )
            
            # Next request should be rate limited
            response = api_client.post(
                download_url,
                {'url': 'https://www.instagram.com/p/valid/'},
                format='json'
            )
            
            assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_concurrent_requests(self, api_client, download_url):
        """Test handling of concurrent requests"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            response = api_client.post(
                download_url,
                {'url': 'https://www.instagram.com/p/valid/'},
                format='json'
            )
            results.put(response.status_code)
        
        # Create multiple threads
        threads = [
            threading.Thread(target=make_request)
            for _ in range(10)
        ]
        
        # Start threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check results
        status_codes = []
        while not results.empty():
            status_codes.append(results.get())
        
        assert all(code == status.HTTP_202_ACCEPTED for code in status_codes)