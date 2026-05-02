from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    ConsumerRegisterSerializer,
    EmailTokenObtainPairSerializer,
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
            {"success": True, "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = EmailTokenObtainPairSerializer


class RefreshTokenView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({"success": True, "user": UserSerializer(request.user).data})

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
        return Response({"success": True, "user": UserSerializer(user).data})
