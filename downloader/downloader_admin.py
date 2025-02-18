from django.contrib import admin
from .models import UserProfile, DownloadedMedia

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'download_quota', 'downloads_today', 'is_premium')
    search_fields = ('user__username', 'user__email')
    list_filter = ('is_premium',)

@admin.register(DownloadedMedia)
class DownloadedMediaAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'media_type', 'status',
        'created_at', 'file_size', 'quality'
    )
    list_filter = ('status', 'media_type', 'quality')
    search_fields = ('user__username', 'url')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)