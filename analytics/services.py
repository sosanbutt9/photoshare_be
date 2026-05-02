from django.contrib.auth import get_user_model

from media_posts.models import Photo

User = get_user_model()


def recent_users(limit: int = 10):
    return list(
        User.objects.order_by("-created_at").values(
            "id",
            "email",
            "username",
            "full_name",
            "role",
            "created_at",
        )[:limit]
    )


def recent_photos(limit: int = 10):
    return list(
        Photo.objects.select_related("creator")
        .order_by("-created_at")
        .values(
            "id",
            "title",
            "creator_id",
            "creator__username",
            "view_count",
            "created_at",
        )[:limit]
    )


def platform_summary():
    from comments.models import Comment
    from ratings.models import Rating

    return {
        "total_users": User.objects.count(),
        "total_creators": User.objects.filter(role=User.Role.CREATOR).count(),
        "total_consumers": User.objects.filter(role=User.Role.CONSUMER).count(),
        "total_admins": User.objects.filter(role=User.Role.ADMIN).count(),
        "blocked_users": User.objects.filter(is_blocked=True).count(),
        "total_photos": Photo.objects.count(),
        "total_comments": Comment.objects.count(),
        "total_ratings": Rating.objects.count(),
    }
