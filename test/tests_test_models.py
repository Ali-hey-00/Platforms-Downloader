import pytest
from django.core.exceptions import ValidationError
from downloader.models import Download
from django.utils import timezone
import os

pytestmark = pytest.mark.django_db

class TestDownloadModel:
    """Test suite for Download model"""

    def test_create_download(self, create_test_download):
        """Test creating a download instance"""
        download = create_test_download()
        assert download.pk is not None
        assert download.status == Download.Status.PENDING
        assert download.created_at is not None

    def test_invalid_url_validation(self):
        """Test validation of non-Instagram URLs"""
        with pytest.raises(ValidationError) as exc:
            Download(url='https://example.com/invalid').clean()
        assert 'URL must be from Instagram' in str(exc.value)

    def test_file_operations(self, create_test_download, temp_media_root):
        """Test file-related operations"""
        download = create_test_download(
            file_path='test/image.jpg',
            status=Download.Status.COMPLETED
        )
        
        # Test file name extraction
        assert download.get_file_name() == 'image.jpg'
        assert download.get_file_extension() == '.jpg'
        
        # Test full path
        expected_path = os.path.join(temp_media_root, 'test/image.jpg')
        assert download.get_download_path() == expected_path

    def test_download_count_increment(self, create_test_download):
        """Test download counter increment"""
        download = create_test_download()
        initial_count = download.download_count
        
        download.increment_download_count()
        download.refresh_from_db()
        
        assert download.download_count == initial_count + 1

    def test_status_properties(self, create_test_download):
        """Test status-related properties"""
        download = create_test_download()
        
        # Test pending
        assert not download.is_completed
        assert not download.is_failed
        assert not download.is_processing
        
        # Test processing
        download.status = Download.Status.DOWNLOADING
        download.save()
        assert download.is_processing
        
        # Test completed
        download.status = Download.Status.COMPLETED
        download.completed_at = timezone.now()
        download.save()
        assert download.is_completed
        assert download.duration is not None

    @pytest.mark.parametrize('url,expected_valid', [
        ('https://www.instagram.com/p/valid/', True),
        ('https://instagram.com/p/valid/', True),
        ('https://www.instagr.am/p/valid/', True),
        ('https://example.com/invalid/', False),
    ])
    def test_url_validation(self, url, expected_valid):
        """Test URL validation with various inputs"""
        download = Download(url=url)
        
        if expected_valid:
            download.clean()  # Should not raise
        else:
            with pytest.raises(ValidationError):
                download.clean()

    def test_concurrent_download_count_increment(self, create_test_download):
        """Test concurrent download count increments"""
        download = create_test_download()
        
        # Simulate concurrent increments
        for _ in range(5):
            download.increment_download_count()
        
        download.refresh_from_db()
        assert download.download_count == 5