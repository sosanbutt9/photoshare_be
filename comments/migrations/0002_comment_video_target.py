# Generated manually

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("comments", "0001_initial"),
        ("media_posts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="video",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments",
                to="media_posts.video",
            ),
        ),
        migrations.AlterField(
            model_name="comment",
            name="photo",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments",
                to="media_posts.photo",
            ),
        ),
        migrations.AddIndex(
            model_name="comment",
            index=models.Index(fields=["video", "created_at"], name="comments_co_video_i_idx"),
        ),
        migrations.AddConstraint(
            model_name="comment",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(photo__isnull=False, video__isnull=True)
                    | models.Q(photo__isnull=True, video__isnull=False)
                ),
                name="comment_target_photo_or_video",
            ),
        ),
    ]
