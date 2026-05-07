from django.conf import settings
from django.db import models


class Comment(models.Model):
    photo = models.ForeignKey(
        "media_posts.Photo",
        on_delete=models.CASCADE,
        related_name="comments",
        db_index=True,
        null=True,
        blank=True,
    )
    video = models.ForeignKey(
        "media_posts.Video",
        on_delete=models.CASCADE,
        related_name="comments",
        db_index=True,
        null=True,
        blank=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="photo_comments",
        db_index=True,
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["photo", "created_at"]),
            models.Index(fields=["video", "created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(photo__isnull=False, video__isnull=True)
                    | models.Q(photo__isnull=True, video__isnull=False)
                ),
                name="comment_target_photo_or_video",
            ),
        ]

    def __str__(self):
        if self.photo_id:
            return f"Comment {self.pk} on photo {self.photo_id}"
        return f"Comment {self.pk} on video {self.video_id}"
