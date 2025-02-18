import os
import uuid
from django.db import models
from django.core.validators import URLValidator, FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Download(models.Model):
    """Model for tracking download requests and their status."""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        DOWNLOADING = 'DOWNLOADING', _('Downloading')
        PROCESSING = 'PROCESSING', _('Processing')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')

    class MediaType(models.TextChoices):
        IMAGE = 'IMAGE', _('Image')
        VIDEO = 'VIDEO', _('Video')
        GALLERY = 'GALLERY', _('Gallery')
        UNKNOWN = 'UNKNOWN', _('Unknown')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_('Unique identifier for the download')
    )

    url = models.URLField(
        max_length=2048,
        validators=[URLValidator(schemes=['http', 'https'])],
        help_text=_('Instagram media URL to download')
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text=_('Current status of the download')
    )

    media_type = models.CharField(
        max_length=20,
        choices=MediaType.choices,
        default=MediaType.UNKNOWN,
        help_text=_('Type of media being downloaded')
    )

    file_path = models.CharField(
        max_length=512,
        blank=True,
        help_text=_('Path to the downloaded file')
    )

    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        help_text=_('Size of the downloaded file in bytes')
    )

    mime_type = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('MIME type of the downloaded file')
    )

    error_message = models.TextField(
        blank=True,
        help_text=_('Error message if download failed')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text=_('Timestamp when download was requested')
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_('Timestamp when download was last updated')
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Timestamp when download was completed')
    )

    download_count = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of times this media has been downloaded')
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text=_('IP address of the requester')
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['url']),
            models.Index(fields=['media_type']),
        ]
        verbose_name = _('Download')
        verbose_name_plural = _('Downloads')

    def __str__(self):
        return f"{self.url} - {self.status}"

    def get_file_name(self):
        """Get the filename from the file path."""
        if self.file_path:
            return os.path.basename(self.file_path)
        return None

    def get_file_extension(self):
        """Get the file extension."""
        if self.file_path:
            return os.path.splitext(self.file_path)[1].lower()
        return None

    def get_download_path(self):
        """Get the full path to the downloaded file."""
        if self.file_path:
            return os.path.join(settings.MEDIA_ROOT, self.file_path)
        return None

    def increment_download_count(self):
        """Increment the download counter."""
        self.download_count = models.F('download_count') + 1
        self.save(update_fields=['download_count'])

    def clean(self):
        """Validate the model."""
        from django.core.exceptions import ValidationError
        
        # Validate URL
        if self.url and not any(domain in self.url.lower() 
                               for domain in ['instagram.com', 'instagr.am']):
            raise ValidationError({
                'url': _('URL must be from Instagram')
            })

    def save(self, *args, **kwargs):
        """Override save method to perform additional operations."""
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_completed(self):
        """Check if download is completed."""
        return self.status == self.Status.COMPLETED

    @property
    def is_failed(self):
        """Check if download failed."""
        return self.status == self.Status.FAILED

    @property
    def is_processing(self):
        """Check if download is in progress."""
        return self.status in [
            self.Status.DOWNLOADING,
            self.Status.PROCESSING
        ]

    @property
    def duration(self):
        """Calculate download duration in seconds."""
        if self.completed_at and self.created_at:
            return (self.completed_at - self.created_at).total_seconds()
        return None