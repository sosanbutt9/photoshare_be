from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Rating(models.Model):
    photo = models.ForeignKey(
        "media_posts.Photo",
        on_delete=models.CASCADE,
        related_name="ratings",
        db_index=True,
        null=True,
        blank=True,
    )
    video = models.ForeignKey(
        "media_posts.Video",
        on_delete=models.CASCADE,
        related_name="ratings",
        db_index=True,
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="photo_ratings",
        db_index=True,
    )
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["photo", "user"],
                condition=models.Q(photo__isnull=False),
                name="unique_rating_per_user_per_photo",
            ),
            models.UniqueConstraint(
                fields=["video", "user"],
                condition=models.Q(video__isnull=False),
                name="unique_rating_per_user_per_video",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(photo__isnull=False, video__isnull=True)
                    | models.Q(photo__isnull=True, video__isnull=False)
                ),
                name="rating_target_photo_or_video",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        if self.photo_id:
            return f"{self.user_id} → photo {self.photo_id}: {self.score}"
        return f"{self.user_id} → video {self.video_id}: {self.score}"
