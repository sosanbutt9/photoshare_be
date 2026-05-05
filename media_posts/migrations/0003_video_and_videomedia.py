from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("media_posts", "0002_photomedia"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Video",
            fields=[
                (
                    "id",
                    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("title", models.CharField(max_length=255)),
                ("caption", models.TextField(blank=True)),
                ("video", models.FileField(upload_to="videos/%Y/%m/")),
                ("location", models.CharField(blank=True, max_length=255)),
                ("people_present", models.CharField(blank=True, max_length=512)),
                ("view_count", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "creator",
                    models.ForeignKey(
                        db_index=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="videos",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [models.Index(fields=["-created_at"], name="media_posts_created_6ec0c3_idx")],
            },
        ),
        migrations.CreateModel(
            name="VideoMedia",
            fields=[
                (
                    "id",
                    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("file", models.FileField(upload_to="videos/%Y/%m/")),
                ("sort_order", models.PositiveSmallIntegerField(db_index=True, default=0)),
                (
                    "video_post",
                    models.ForeignKey(
                        db_index=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="media_items",
                        to="media_posts.video",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order", "id"],
            },
        ),
    ]
