from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserFollow, UserRole
from .services import RegistrationError, register_consumer

User = get_user_model()


def _absolute_avatar_url(request, user):
    if not user.avatar:
        return ""
    if request:
        return request.build_absolute_uri(user.avatar.url)
    return user.avatar.url


class FollowListUserSerializer(serializers.ModelSerializer):
    """Minimal user row for followers / following lists."""

    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "full_name", "avatar")
        read_only_fields = fields

    def get_avatar(self, obj):
        return _absolute_avatar_url(self.context.get("request"), obj)


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "full_name",
            "avatar",
            "role",
            "is_blocked",
            "is_superuser",
            "followers_count",
            "following_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_avatar(self, obj):
        return _absolute_avatar_url(self.context.get("request"), obj)

    def get_followers_count(self, obj):
        return UserFollow.objects.filter(following=obj).count()

    def get_following_count(self, obj):
        return UserFollow.objects.filter(follower=obj).count()


class PublicProfileSerializer(serializers.ModelSerializer):
    """Another member's profile (public GET)."""

    avatar = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "full_name",
            "avatar",
            "role",
            "followers_count",
            "following_count",
            "is_following",
            "created_at",
        )
        read_only_fields = fields

    def get_avatar(self, obj):
        return _absolute_avatar_url(self.context.get("request"), obj)

    def get_followers_count(self, obj):
        return UserFollow.objects.filter(following=obj).count()

    def get_following_count(self, obj):
        return UserFollow.objects.filter(follower=obj).count()

    def get_is_following(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        if request.user.pk == obj.pk:
            return False
        return UserFollow.objects.filter(follower=request.user, following=obj).exists()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Authenticated user may update display identity fields (not role or flags)."""

    class Meta:
        model = User
        fields = ("username", "full_name", "email", "avatar")
        extra_kwargs = {"avatar": {"required": False, "allow_null": True}}

    def validate_username(self, value):
        if not value or not str(value).strip():
            raise serializers.ValidationError("Username cannot be blank.")
        cleaned = str(value).strip()
        if (
            User.objects.exclude(pk=self.instance.pk)
            .filter(username__iexact=cleaned)
            .exists()
        ):
            raise serializers.ValidationError("This username is already taken.")
        return cleaned

    def validate_email(self, value):
        norm = User.objects.normalize_email(str(value).strip())
        if (
            User.objects.exclude(pk=self.instance.pk)
            .filter(email__iexact=norm)
            .exists()
        ):
            raise serializers.ValidationError("An account with this email already exists.")
        return norm

    def validate_full_name(self, value):
        if value is None:
            return ""
        return str(value).strip()


class ConsumerRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    full_name = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    role = serializers.ChoiceField(
        choices=[UserRole.CONSUMER, UserRole.CREATOR],
        default=UserRole.CONSUMER,
        required=False,
    )

    def validate_username(self, value):
        if not value.strip():
            raise serializers.ValidationError("Username cannot be blank.")
        return value.strip()

    def create(self, validated_data):
        try:
            return register_consumer(
                email=validated_data["email"],
                username=validated_data["username"],
                password=validated_data["password"],
                full_name=validated_data.get("full_name", ""),
                role=validated_data.get("role") or UserRole.CONSUMER,
            )
        except RegistrationError as exc:
            raise serializers.ValidationError({"detail": exc.message, "code": exc.code}) from exc


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        if user.is_blocked:
            raise serializers.ValidationError(
                {"detail": "This account has been blocked. Contact support if you believe this is an error."}
            )
        data["user"] = UserSerializer(user, context=self.context).data
        return data
