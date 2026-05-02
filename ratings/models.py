from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Rating(models.Model):
    photo = models.ForeignKey(
        "media_posts.Photo",
        on_delete=models.CASCADE,
        related_name="ratings",
        db_index=True,
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
            models.UniqueConstraint(fields=["photo", "user"], name="unique_rating_per_user_per_photo"),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user_id} → {self.photo_id}: {self.score}"
