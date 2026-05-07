from django.urls import path

from .views import (
    FollowUserView,
    LoginView,
    MeView,
    RefreshTokenView,
    RegisterView,
    UserPublicProfileView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("token/refresh/", RefreshTokenView.as_view(), name="auth-token-refresh"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("users/<int:user_id>/", UserPublicProfileView.as_view(), name="auth-user-profile"),
    path("users/<int:user_id>/follow/", FollowUserView.as_view(), name="auth-user-follow"),
]
