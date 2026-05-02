from django.urls import include, path
from rest_framework.routers import DefaultRouter

from analytics.views import AdminStatsView
from comments.views import CommentViewSet
from media_posts.views import PhotoViewSet

router = DefaultRouter()
router.register(r"photos", PhotoViewSet, basename="photo")
router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = [
    path("auth/", include("accounts.urls")),
    path("admin/stats/", AdminStatsView.as_view(), name="admin-stats"),
    path("", include(router.urls)),
]
