from django.db.models import F

from .models import MediaLike, Photo, Video


def increment_photo_view_count(photo: Photo) -> None:
    Photo.objects.filter(pk=photo.pk).update(view_count=F("view_count") + 1)
    photo.refresh_from_db(fields=["view_count"])


def increment_video_view_count(video_post: Video) -> None:
    Video.objects.filter(pk=video_post.pk).update(view_count=F("view_count") + 1)
    video_post.refresh_from_db(fields=["view_count"])


def toggle_photo_like(*, user, photo: Photo) -> tuple[bool, int]:
    """Toggle like; returns (liked_after_toggle, likes_count)."""
    existing = MediaLike.objects.filter(user=user, photo=photo).first()
    if existing:
        existing.delete()
        liked = False
    else:
        MediaLike.objects.create(user=user, photo=photo)
        liked = True
    count = MediaLike.objects.filter(photo=photo).count()
    return liked, count


def toggle_video_like(*, user, video_post: Video) -> tuple[bool, int]:
    existing = MediaLike.objects.filter(user=user, video=video_post).first()
    if existing:
        existing.delete()
        liked = False
    else:
        MediaLike.objects.create(user=user, video=video_post)
        liked = True
    count = MediaLike.objects.filter(video=video_post).count()
    return liked, count
