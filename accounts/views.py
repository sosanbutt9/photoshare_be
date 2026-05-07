from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User, UserFollow
from .serializers import (
    ConsumerRegisterSerializer,
    EmailTokenObtainPairSerializer,
    PublicProfileSerializer,
    UserProfileUpdateSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    """Consumer self-registration only."""

    serializer_class = ConsumerRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"success": True, "user": UserSerializer(user, context={"request": request}).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = EmailTokenObtainPairSerializer


class RefreshTokenView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        return Response(
            {"success": True, "user": UserSerializer(request.user, context={"request": request}).data}
        )

    def patch(self, request):
        user = request.user
        if user.is_blocked:
            return Response(
                {"success": False, "detail": "This account has been blocked."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user.refresh_from_db()
        return Response(
            {"success": True, "user": UserSerializer(user, context={"request": request}).data}
        )


class UserPublicProfileView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id):
        profile_user = get_object_or_404(User.objects.all(), pk=user_id)
        return Response(
            {
                "success": True,
                "user": PublicProfileSerializer(profile_user, context={"request": request}).data,
            }
        )


class FollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        target = get_object_or_404(User.objects.all(), pk=user_id)
        if target.pk == request.user.pk:
            return Response(
                {"success": False, "detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        UserFollow.objects.get_or_create(follower=request.user, following=target)
        return Response({"success": True, "following": True})

    def delete(self, request, user_id):
        target = get_object_or_404(User.objects.all(), pk=user_id)
        UserFollow.objects.filter(follower=request.user, following=target).delete()
        return Response({"success": True, "following": False})
