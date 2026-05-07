from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Comment

User = get_user_model()


class CommentAuthorSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "full_name", "avatar")
        read_only_fields = fields

    def get_avatar(self, obj):
        if not getattr(obj, "avatar", None):
            return ""
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.avatar.url)
        return obj.avatar.url


class CommentSerializer(serializers.ModelSerializer):
    author = CommentAuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "photo", "video", "author", "body", "created_at", "updated_at")
        read_only_fields = ("id", "photo", "video", "author", "created_at", "updated_at")


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("body",)

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        photo = self.context.get("photo")
        video = self.context.get("video")
        if photo is not None:
            validated_data["photo"] = photo
        elif video is not None:
            validated_data["video"] = video
        else:
            raise serializers.ValidationError({"detail": "No comment target provided."})
        return super().create(validated_data)
