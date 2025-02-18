import os
import pytest
from django.conf import settings
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from downloader.models import Download
from unittest.mock import patch
import redis
import tempfile

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Configure test database"""
    with django_db_blocker.unblock():
        # Custom DB setup if needed
        pass

@pytest.fixture
def api_client():
    """Create a test API client"""
    return APIClient()

@pytest.fixture
def mock_redis():
    """Mock Redis connection"""
    with patch('django_redis.get_redis_connection') as mock:
        yield mock

@pytest.fixture
def temp_media_root(settings):
    """Create temporary media root for tests"""
    temp_dir = tempfile.mkdtemp()
    settings.MEDIA_ROOT = temp_dir
    yield temp_dir
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_instagram_url():
    """Sample Instagram post URL"""
    return "https://www.instagram.com/p/sample_post/"

@pytest.fixture
def mock_successful_download():
    """Mock successful download response"""
    return {
        'url': 'https://www.instagram.com/p/sample_post/',
        'media_type': 'IMAGE',
        'file_size': 1024,
        'mime_type': 'image/jpeg',
        'filename': 'test_image.jpg'
    }

@pytest.fixture
def create_test_download():
    """Create a test download instance"""
    def _create_download(**kwargs):
        defaults = {
            'url': 'https://www.instagram.com/p/sample_post/',
            'status': Download.Status.PENDING,
            'media_type': Download.MediaType.IMAGE
        }
        defaults.update(kwargs)
        return Download.objects.create(**defaults)
    return _create_download