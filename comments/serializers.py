from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Comment

User = get_user_model()


class CommentAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "full_name")
        read_only_fields = fields


class CommentSerializer(serializers.ModelSerializer):
    author = CommentAuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "photo", "author", "body", "created_at", "updated_at")
        read_only_fields = ("id", "photo", "author", "created_at", "updated_at")


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("body",)

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        validated_data["photo"] = self.context["photo"]
        return super().create(validated_data)
