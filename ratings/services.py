from django.db import transaction

from .models import Rating


@transaction.atomic
def set_photo_rating(*, user, photo, score: int) -> tuple[Rating, bool]:
    """
    Create or update the user's rating for a photo.
    Returns (rating_instance, created_bool).
    """
    rating, created = Rating.objects.get_or_create(
        user=user,
        photo=photo,
        defaults={"score": score},
    )
    if not created:
        rating.score = score
        rating.save(update_fields=["score", "updated_at"])
    return rating, created


@transaction.atomic
def set_video_rating(*, user, video, score: int) -> tuple[Rating, bool]:
    """Create or update the user's rating for a video post."""
    rating, created = Rating.objects.get_or_create(
        user=user,
        video=video,
        defaults={"score": score},
    )
    if not created:
        rating.score = score
        rating.save(update_fields=["score", "updated_at"])
    return rating, created
