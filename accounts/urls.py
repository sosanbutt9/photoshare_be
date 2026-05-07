from django.urls import path

from .views import (
    FollowUserView,
    LoginView,
    MeView,
    RefreshTokenView,
    RegisterView,
    UserFollowersListView,
    UserFollowingListView,
    UserPublicProfileView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("token/refresh/", RefreshTokenView.as_view(), name="auth-token-refresh"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("users/<int:user_id>/followers/", UserFollowersListView.as_view(), name="auth-user-followers"),
    path("users/<int:user_id>/following/", UserFollowingListView.as_view(), name="auth-user-following"),
    path("users/<int:user_id>/follow/", FollowUserView.as_view(), name="auth-user-follow"),
    path("users/<int:user_id>/", UserPublicProfileView.as_view(), name="auth-user-profile"),
]
