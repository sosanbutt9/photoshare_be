# Generated manually

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("media_posts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MediaLike",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "photo",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="likes",
                        to="media_posts.photo",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="media_likes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "video",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="likes",
                        to="media_posts.video",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="medialike",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(photo__isnull=False, video__isnull=True)
                    | models.Q(photo__isnull=True, video__isnull=False)
                ),
                name="like_target_photo_or_video",
            ),
        ),
        migrations.AddConstraint(
            model_name="medialike",
            constraint=models.UniqueConstraint(
                condition=models.Q(photo__isnull=False),
                fields=("user", "photo"),
                name="unique_like_user_photo",
            ),
        ),
        migrations.AddConstraint(
            model_name="medialike",
            constraint=models.UniqueConstraint(
                condition=models.Q(video__isnull=False),
                fields=("user", "video"),
                name="unique_like_user_video",
            ),
        ),
    ]
