from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import UserProfile, DownloadedMedia
from unittest.mock import patch

class MediaDownloadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)
        self.valid_url = 'https://www.instagram.com/p/example/'

    def test_download_request_success(self):
        data = {'url': self.valid_url, 'quality': 'high'}
        response = self.client.post(reverse('download'), data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(DownloadedMedia.objects.filter(user=self.user).exists())

    @patch('downloader.tasks.download_media.delay')
    def test_download_request_quota_exceeded(self, mock_task):
        self.profile.download_quota = 0
        self.profile.save()
        
        data = {'url': self.valid_url, 'quality': 'high'}
        response = self.client.post(reverse('download'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        mock_task.assert_not_called()