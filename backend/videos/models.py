from django.db import models
from django.conf import settings


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name


class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True, related_name='videos')
    original_file = models.FileField(upload_to='videos/originals/')
    jellyfin_item_id = models.CharField(max_length=64, blank=True, default='')
    duration_seconds = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # Generated assets
    thumbnail = models.ImageField(upload_to='videos/thumbnails/', blank=True, null=True)
    hls_master_playlist = models.FileField(upload_to='videos/hls/', blank=True, null=True)

    def __str__(self) -> str:
        return self.title


class SavedVideo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_videos')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video')


