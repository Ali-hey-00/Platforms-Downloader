from rest_framework import serializers
from .models import Download
from .services.validator import validate_instagram_url

class DownloadSerializer(serializers.ModelSerializer):
    file_name = serializers.CharField(source='get_file_name', read_only=True)
    duration = serializers.FloatField(read_only=True)
    file_size_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Download
        fields = [
            'id', 'url', 'status', 'file_name', 'error_message',
            'created_at', 'updated_at', 'duration', 'file_size',
            'file_size_formatted'
        ]
        read_only_fields = [
            'id', 'status', 'file_name', 'error_message',
            'created_at', 'updated_at', 'duration', 'file_size',
            'file_size_formatted'
        ]

    def get_file_size_formatted(self, obj):
        """Convert file size to human-readable format"""
        if not obj.file_size:
            return None
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if obj.file_size < 1024.0:
                return f"{obj.file_size:.1f} {unit}"
            obj.file_size /= 1024.0
        return f"{obj.file_size:.1f} TB"

    def validate_url(self, value):
        """Validate Instagram URL"""
        if not validate_instagram_url(value):
            raise serializers.ValidationError(
                "Invalid Instagram URL. Please provide a valid Instagram post URL."
            )
        return value