# Generated manually

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("media_posts", "0001_initial"),
        ("ratings", "0001_initial"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="rating",
            name="unique_rating_per_user_per_photo",
        ),
        migrations.AddField(
            model_name="rating",
            name="video",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ratings",
                to="media_posts.video",
            ),
        ),
        migrations.AlterField(
            model_name="rating",
            name="photo",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ratings",
                to="media_posts.photo",
            ),
        ),
        migrations.AddConstraint(
            model_name="rating",
            constraint=models.UniqueConstraint(
                condition=models.Q(photo__isnull=False),
                fields=("photo", "user"),
                name="unique_rating_per_user_per_photo",
            ),
        ),
        migrations.AddConstraint(
            model_name="rating",
            constraint=models.UniqueConstraint(
                condition=models.Q(video__isnull=False),
                fields=("video", "user"),
                name="unique_rating_per_user_per_video",
            ),
        ),
        migrations.AddConstraint(
            model_name="rating",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(photo__isnull=False, video__isnull=True)
                    | models.Q(photo__isnull=True, video__isnull=False)
                ),
                name="rating_target_photo_or_video",
            ),
        ),
    ]
