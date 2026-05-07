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


class Video(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="videos",
        db_index=True,
    )
    title = models.CharField(max_length=255)
    caption = models.TextField(blank=True)
    video = models.FileField(upload_to="videos/%Y/%m/")
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


class VideoMedia(models.Model):
    """Additional clips for a post (carousel). First clip is always ``Video.video``."""

    video_post = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="media_items",
        db_index=True,
    )
    file = models.FileField(upload_to="videos/%Y/%m/")
    sort_order = models.PositiveSmallIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.video_post_id}:{self.sort_order}"


class MediaLike(models.Model):
    """A single like on a photo or a video (not both)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="media_likes",
        db_index=True,
    )
    photo = models.ForeignKey(
        Photo,
        on_delete=models.CASCADE,
        related_name="likes",
        db_index=True,
        null=True,
        blank=True,
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="likes",
        db_index=True,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(photo__isnull=False, video__isnull=True)
                    | models.Q(photo__isnull=True, video__isnull=False)
                ),
                name="like_target_photo_or_video",
            ),
            models.UniqueConstraint(
                fields=["user", "photo"],
                condition=models.Q(photo__isnull=False),
                name="unique_like_user_photo",
            ),
            models.UniqueConstraint(
                fields=["user", "video"],
                condition=models.Q(video__isnull=False),
                name="unique_like_user_video",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"like {self.user_id}"
