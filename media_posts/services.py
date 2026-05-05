from django.db.models import F

from .models import Photo, Video


def increment_photo_view_count(photo: Photo) -> None:
    Photo.objects.filter(pk=photo.pk).update(view_count=F("view_count") + 1)
    photo.refresh_from_db(fields=["view_count"])


def increment_video_view_count(video_post: Video) -> None:
    Video.objects.filter(pk=video_post.pk).update(view_count=F("view_count") + 1)
    video_post.refresh_from_db(fields=["view_count"])
