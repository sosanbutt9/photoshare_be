from django.conf import settings
from django.db import models


class Photo(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="photos",
        db_index=True,
    )
    title = models.CharField(max_length=255)
    caption = models.TextField(blank=True)
    image = models.ImageField(upload_to="photos/%Y/%m/")
    location = models.CharField(max_length=255, blank=True)
    people_present = models.CharField(max_length=512, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return self.title


class PhotoMedia(models.Model):
    """Additional images for a post (carousel). First slide is always ``Photo.image``."""

    photo = models.ForeignKey(
        Photo,
        on_delete=models.CASCADE,
        related_name="media_items",
        db_index=True,
    )
    image = models.ImageField(upload_to="photos/%Y/%m/")
    sort_order = models.PositiveSmallIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.photo_id}:{self.sort_order}"
