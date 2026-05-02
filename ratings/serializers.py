from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Rating

User = get_user_model()


class RatingUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "full_name")
        read_only_fields = fields


class RatingSerializer(serializers.ModelSerializer):
    user = RatingUserSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = ("id", "photo", "user", "score", "created_at", "updated_at")
        read_only_fields = ("id", "photo", "user", "created_at", "updated_at")
