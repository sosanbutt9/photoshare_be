from django.conf import settings
from django.db import models


class Comment(models.Model):
    photo = models.ForeignKey(
        "media_posts.Photo",
        on_delete=models.CASCADE,
        related_name="comments",
        db_index=True,
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
        ]

    def __str__(self):
        return f"Comment {self.pk} on photo {self.photo_id}"
