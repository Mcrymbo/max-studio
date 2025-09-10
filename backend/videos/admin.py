from django.contrib import admin
from .models import Video, Genre, SavedVideo


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "created_at", "is_active")
    list_filter = ("genre", "is_active")
    search_fields = ("title", "description")


@admin.register(SavedVideo)
class SavedVideoAdmin(admin.ModelAdmin):
    list_display = ("user", "video", "created_at")
    search_fields = ("user__username", "video__title")





