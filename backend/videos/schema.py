import os
import shutil
import time
from typing import List, Optional

import graphene
from graphene_django import DjangoObjectType
from django.conf import settings
from django.db import transaction
from django.contrib.auth import get_user_model

from .models import Video, Genre, SavedVideo
from .jellyfin_client import JellyfinClient, build_signed_url


class VideoType(DjangoObjectType):
    class Meta:
        model = Video
        fields = (
            "id",
            "title",
            "description",
            "genre",
            "duration_seconds",
            "jellyfin_item_id",
            "created_at",
        )


class GQLVideo(graphene.ObjectType):
    id = graphene.ID()
    title = graphene.String()
    description = graphene.String()
    duration_seconds = graphene.Int()
    thumbnail_url = graphene.String()
    playback_url = graphene.String(description="Signed HLS master.m3u8 URL via Django proxy")
    genre = graphene.String()


class VideosQuery(graphene.ObjectType):
    videos = graphene.List(GQLVideo, genre=graphene.String(required=False))
    video = graphene.Field(GQLVideo, id=graphene.ID(required=True))

    def _client(self) -> JellyfinClient:
        return JellyfinClient(settings.JELLYFIN_URL, settings.JELLYFIN_API_KEY, settings.JELLYFIN_USER_ID)

    def resolve_videos(self, info, genre=None):
        client = self._client()
        items = client.list_items()
        results: List[GQLVideo] = []
        for it in items:
            item_id = it.get('Id')
            title = it.get('Name')
            overview = it.get('Overview') or ''
            runtime_ticks = it.get('RunTimeTicks') or 0
            duration_seconds = int(runtime_ticks / 10_000_000) if runtime_ticks else 0
            thumb_url = f"{settings.JELLYFIN_URL}/Items/{item_id}/Images/Primary?quality=80&fillHeight=540&fillWidth=960"
            proxy_path = f"/stream/{item_id}/master.m3u8"
            playback_signed = build_signed_url(proxy_path, settings.SIGNED_URL_TTL_SECONDS)
            first_genre = None
            genres = it.get('Genres') or []
            if genres:
                first_genre = genres[0]
            results.append(GQLVideo(
                id=item_id,
                title=title,
                description=overview,
                duration_seconds=duration_seconds,
                thumbnail_url=thumb_url,
                playback_url=playback_signed,
                genre=first_genre,
            ))
        if genre:
            results = [r for r in results if (r.genre or '').lower() == genre.lower()]
        return results

    def resolve_video(self, info, id):
        client = self._client()
        it = client.get_item(id)
        runtime_ticks = it.get('RunTimeTicks') or 0
        duration_seconds = int(runtime_ticks / 10_000_000) if runtime_ticks else 0
        thumb_url = f"{settings.JELLYFIN_URL}/Items/{id}/Images/Primary?quality=80&fillHeight=540&fillWidth=960"
        proxy_path = f"/stream/{id}/master.m3u8"
        playback_signed = build_signed_url(proxy_path, settings.SIGNED_URL_TTL_SECONDS)
        first_genre = None
        genres = it.get('Genres') or []
        if genres:
            first_genre = genres[0]
        return GQLVideo(
            id=id,
            title=it.get('Name'),
            description=it.get('Overview') or '',
            duration_seconds=duration_seconds,
            thumbnail_url=thumb_url,
            playback_url=playback_signed,
            genre=first_genre,
        )


class UploadVideo(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=False)
        genre_name = graphene.String(required=False)
        file = graphene.String(required=True, description="Path to local file on server for now")

    ok = graphene.Boolean()
    video = graphene.Field(VideoType, description="Video record referencing Jellyfin item")

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info, title, file, description=None, genre_name=None):
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            raise Exception("Admin authentication required")

        genre = None
        if genre_name:
            genre, _ = Genre.objects.get_or_create(name=genre_name)

        # Copy into Jellyfin library directory
        original_name = os.path.basename(file)
        library_path = settings.JELLYFIN_LIBRARY_PATH
        os.makedirs(library_path, exist_ok=True)
        dest_path = os.path.join(library_path, original_name)
        shutil.copyfile(file, dest_path)

        client = JellyfinClient(settings.JELLYFIN_URL, settings.JELLYFIN_API_KEY, settings.JELLYFIN_USER_ID)
        client.refresh_library()
        time.sleep(2)

        # Try to find the item by Name or Path
        jellyfin_item_id: Optional[str] = None
        items = client.list_items()
        for it in items:
            if it.get('Name') == title or (it.get('Path') and os.path.basename(it.get('Path')) == original_name):
                jellyfin_item_id = it.get('Id')
                break

        video = Video.objects.create(
            title=title,
            description=description or '',
            genre=genre,
            original_file=original_name,
            jellyfin_item_id=jellyfin_item_id or '',
        )
        return UploadVideo(ok=True, video=video)


class SaveVideo(graphene.Mutation):
    class Arguments:
        video_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, video_id):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        video = Video.objects.filter(jellyfin_item_id=video_id).first() or Video.objects.filter(id=video_id).first()
        if not video:
            # Create a lightweight placeholder referencing Jellyfin only
            video = Video.objects.create(title="", description="", jellyfin_item_id=video_id)
        SavedVideo.objects.get_or_create(user=user, video=video)
        return SaveVideo(ok=True)


class UnsaveVideo(graphene.Mutation):
    class Arguments:
        video_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, video_id):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        SavedVideo.objects.filter(user=user, video__jellyfin_item_id=video_id).delete()
        SavedVideo.objects.filter(user=user, video_id=video_id).delete()
        return UnsaveVideo(ok=True)


class VideosMutation(graphene.ObjectType):
    upload_video = UploadVideo.Field()
    save_video = SaveVideo.Field()
    unsave_video = UnsaveVideo.Field()

import os
import subprocess
import uuid
from typing import List

import graphene
from graphene_django import DjangoObjectType
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.contrib.auth import get_user_model

from .models import Video, Genre, SavedVideo


class GenreType(DjangoObjectType):
    class Meta:
        model = Genre
        fields = ("id", "name")


class VideoType(DjangoObjectType):
    class Meta:
        model = Video
        fields = (
            "id",
            "title",
            "description",
            "genre",
            "duration_seconds",
            "thumbnail",
            "hls_master_playlist",
            "created_at",
        )


class VideosQuery(graphene.ObjectType):
    videos = graphene.List(VideoType, genre=graphene.String(required=False))
    video = graphene.Field(VideoType, id=graphene.ID(required=True))

    def resolve_videos(self, info, genre=None):
        qs = Video.objects.filter(is_active=True).order_by('-created_at')
        if genre:
            qs = qs.filter(genre__name__iexact=genre)
        return qs

    def resolve_video(self, info, id):
        return Video.objects.get(pk=id, is_active=True)


class UploadVideo(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=False)
        genre_name = graphene.String(required=False)
        file = graphene.String(required=True, description="Path to local file on server for now")

    ok = graphene.Boolean()
    video = graphene.Field(VideoType)

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info, title, file, description=None, genre_name=None):
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            raise Exception("Admin authentication required")

        genre = None
        if genre_name:
            genre, _ = Genre.objects.get_or_create(name=genre_name)

        video = Video.objects.create(title=title, description=description or '', genre=genre)

        # Save original file
        original_name = os.path.basename(file)
        with open(file, 'rb') as f:
            video.original_file.save(original_name, ContentFile(f.read()))

        # Generate thumbnail and HLS
        generate_assets_for_video(video)

        video.save()
        return UploadVideo(ok=True, video=video)


class SaveVideo(graphene.Mutation):
    class Arguments:
        video_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, video_id):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        video = Video.objects.get(pk=video_id)
        SavedVideo.objects.get_or_create(user=user, video=video)
        return SaveVideo(ok=True)


class UnsaveVideo(graphene.Mutation):
    class Arguments:
        video_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, video_id):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        SavedVideo.objects.filter(user=user, video_id=video_id).delete()
        return UnsaveVideo(ok=True)


class VideosMutation(graphene.ObjectType):
    upload_video = UploadVideo.Field()
    save_video = SaveVideo.Field()
    unsave_video = UnsaveVideo.Field()


def generate_assets_for_video(video: Video) -> None:
    """
    Use ffmpeg to create a thumbnail and HLS variants (480p, 720p, 1080p).
    This is a synchronous helper for now; later we can move to Celery.
    """
    input_path = video.original_file.path
    media_root = settings.MEDIA_ROOT
    uid = uuid.uuid4().hex
    hls_dir = os.path.join(media_root, 'videos', 'hls', uid)
    os.makedirs(hls_dir, exist_ok=True)

    # Thumbnail at 3 seconds
    thumb_path = os.path.join(media_root, 'videos', 'thumbnails', f'{uid}.jpg')
    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
    subprocess.run([
        'ffmpeg', '-y', '-ss', '00:00:03', '-i', input_path, '-vframes', '1', '-vf', 'scale=640:-1', thumb_path
    ], check=True)
    rel_thumb = os.path.relpath(thumb_path, media_root)
    video.thumbnail.name = rel_thumb.replace('\\', '/')

    # Build HLS outputs
    master_playlist_path = os.path.join(hls_dir, 'master.m3u8')
    variant_cmds: List[str] = [
        '-filter:v:0', 'scale=w=854:h=480:force_original_aspect_ratio=decrease', '-c:v:0', 'h264', '-b:v:0', '800k', '-maxrate:v:0', '856k', '-bufsize:v:0', '1200k', '-c:a:0', 'aac', '-b:a:0', '96k',
        '-filter:v:1', 'scale=w=1280:h=720:force_original_aspect_ratio=decrease', '-c:v:1', 'h264', '-b:v:1', '2800k', '-maxrate:v:1', '2996k', '-bufsize:v:1', '4200k', '-c:a:1', 'aac', '-b:a:1', '128k',
        '-filter:v:2', 'scale=w=1920:h=1080:force_original_aspect_ratio=decrease', '-c:v:2', 'h264', '-b:v:2', '5000k', '-maxrate:v:2', '5350k', '-bufsize:v:2', '7500k', '-c:a:2', 'aac', '-b:a:2', '192k',
    ]

    hls_flags = [
        '-f', 'hls', '-hls_playlist_type', 'vod', '-hls_time', '6', '-hls_list_size', '0',
        '-master_pl_name', 'master.m3u8', '-var_stream_map', 'v:0,a:0 v:1,a:1 v:2,a:2',
    ]

    # Output pattern
    out_pattern = os.path.join(hls_dir, '%v', 'index.m3u8')
    os.makedirs(os.path.join(hls_dir, '0'), exist_ok=True)
    os.makedirs(os.path.join(hls_dir, '1'), exist_ok=True)
    os.makedirs(os.path.join(hls_dir, '2'), exist_ok=True)

    cmd = ['ffmpeg', '-y', '-i', input_path, '-map', '0:v:0', '-map', '0:a:0'] + variant_cmds + hls_flags + ['-strftime_mkdir', '1', '-use_localtime_mkdir', '1', out_pattern]
    subprocess.run(cmd, check=True)

    rel_master = os.path.relpath(master_playlist_path, media_root)
    video.hls_master_playlist.name = rel_master.replace('\\', '/')


