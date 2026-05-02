from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Photo, PhotoMedia

User = get_user_model()

MAX_IMAGES_PER_POST = 10


class PhotoCreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "full_name", "email")
        read_only_fields = fields


def _absolute_media_url(request, relative_url):
    if not relative_url:
        return ""
    if request:
        return request.build_absolute_uri(relative_url)
    return relative_url


class PhotoListSerializer(serializers.ModelSerializer):
    creator = PhotoCreatorSerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True, allow_null=True)
    ratings_count = serializers.IntegerField(read_only=True)
    media_count = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = (
            "id",
            "creator",
            "title",
            "caption",
            "image",
            "media_count",
            "location",
            "people_present",
            "view_count",
            "average_rating",
            "ratings_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_media_count(self, obj):
        base = 1 if obj.image else 0
        return base + len(obj.media_items.all())


class PhotoDetailSerializer(PhotoListSerializer):
    """Includes ordered ``media`` URLs for carousel (list endpoints omit this for payload size)."""

    media = serializers.SerializerMethodField()

    class Meta(PhotoListSerializer.Meta):
        fields = PhotoListSerializer.Meta.fields + ("media",)

    def get_media(self, obj):
        request = self.context.get("request")
        urls = []
        if obj.image:
            urls.append(_absolute_media_url(request, obj.image.url))
        for m in obj.media_items.all():
            urls.append(_absolute_media_url(request, m.image.url))
        return urls


class PhotoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ("title", "caption", "image", "location", "people_present")
        extra_kwargs = {"image": {"required": False}}

    def validate(self, attrs):
        request = self.context["request"]
        if self.instance is not None:
            return attrs
        files = request.FILES.getlist("images")
        if not files:
            single = request.FILES.get("image")
            if single:
                files = [single]
        if not files:
            raise serializers.ValidationError(
                {"images": ["Select at least one image."]},
            )
        if len(files) > MAX_IMAGES_PER_POST:
            raise serializers.ValidationError(
                {"images": [f"You can upload at most {MAX_IMAGES_PER_POST} images per post."]},
            )
        attrs["_upload_files"] = files
        return attrs

    def create(self, validated_data):
        files = validated_data.pop("_upload_files")
        validated_data["image"] = files[0]
        validated_data["creator"] = self.context["request"].user
        photo = Photo.objects.create(**validated_data)
        for order, f in enumerate(files[1:], start=1):
            if hasattr(f, "seek"):
                f.seek(0)
            PhotoMedia.objects.create(photo=photo, image=f, sort_order=order)
        return photo


class PhotoRateSerializer(serializers.Serializer):
    score = serializers.IntegerField(min_value=1, max_value=5)
