from django.db.models import F

from .models import Photo


def increment_photo_view_count(photo: Photo) -> None:
    Photo.objects.filter(pk=photo.pk).update(view_count=F("view_count") + 1)
    photo.refresh_from_db(fields=["view_count"])
