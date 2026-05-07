from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Photo, PhotoMedia, Video, VideoMedia

User = get_user_model()

MAX_IMAGES_PER_POST = 10
MAX_VIDEOS_PER_POST = 10


class PhotoCreatorSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "full_name", "email", "avatar")
        read_only_fields = fields

    def get_avatar(self, obj):
        if not getattr(obj, "avatar", None):
            return ""
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.avatar.url)
        return obj.avatar.url


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
    likes_count = serializers.IntegerField(read_only=True)
    liked_by_me = serializers.SerializerMethodField()
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
            "likes_count",
            "liked_by_me",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_liked_by_me(self, obj):
        if hasattr(obj, "liked_by_me"):
            return bool(obj.liked_by_me)
        return False

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
        files = request.FILES.getlist("images")
        if not files:
            single = request.FILES.get("image")
            if single:
                files = [single]

        if self.instance is None:
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

        if files:
            if len(files) > MAX_IMAGES_PER_POST:
                raise serializers.ValidationError(
                    {"images": [f"You can upload at most {MAX_IMAGES_PER_POST} images per update."]},
                )
            attrs["_upload_files"] = files
        else:
            attrs["_upload_files"] = []
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

    def update(self, instance, validated_data):
        files = validated_data.pop("_upload_files", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if files:
            instance.image = files[0]
            instance.save()
            PhotoMedia.objects.filter(photo=instance).delete()
            for order, f in enumerate(files[1:], start=1):
                if hasattr(f, "seek"):
                    f.seek(0)
                PhotoMedia.objects.create(photo=instance, image=f, sort_order=order)
        else:
            instance.save()
        return instance


class PhotoRateSerializer(serializers.Serializer):
    score = serializers.IntegerField(min_value=1, max_value=5)


class VideoListSerializer(serializers.ModelSerializer):
    creator = PhotoCreatorSerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True, allow_null=True)
    ratings_count = serializers.IntegerField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    liked_by_me = serializers.SerializerMethodField()
    media_count = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = (
            "id",
            "creator",
            "title",
            "caption",
            "video",
            "media_count",
            "location",
            "people_present",
            "view_count",
            "average_rating",
            "ratings_count",
            "likes_count",
            "liked_by_me",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_liked_by_me(self, obj):
        if hasattr(obj, "liked_by_me"):
            return bool(obj.liked_by_me)
        return False

    def get_media_count(self, obj):
        base = 1 if obj.video else 0
        return base + len(obj.media_items.all())


class VideoDetailSerializer(VideoListSerializer):
    media = serializers.SerializerMethodField()

    class Meta(VideoListSerializer.Meta):
        fields = VideoListSerializer.Meta.fields + ("media",)

    def get_media(self, obj):
        request = self.context.get("request")
        urls = []
        if obj.video:
            urls.append(_absolute_media_url(request, obj.video.url))
        for m in obj.media_items.all():
            urls.append(_absolute_media_url(request, m.file.url))
        return urls


class VideoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ("title", "caption", "video", "location", "people_present")
        extra_kwargs = {"video": {"required": False}}

    def validate(self, attrs):
        request = self.context["request"]
        files = request.FILES.getlist("videos")
        if not files:
            single = request.FILES.get("video")
            if single:
                files = [single]

        if self.instance is None:
            if not files:
                raise serializers.ValidationError(
                    {"videos": ["Select at least one video."]},
                )
            if len(files) > MAX_VIDEOS_PER_POST:
                raise serializers.ValidationError(
                    {"videos": [f"You can upload at most {MAX_VIDEOS_PER_POST} videos per post."]},
                )
            attrs["_upload_files"] = files
            return attrs

        if files and len(files) > MAX_VIDEOS_PER_POST:
            raise serializers.ValidationError(
                {"videos": [f"You can upload at most {MAX_VIDEOS_PER_POST} videos per update."]},
            )
        attrs["_upload_files"] = files
        return attrs

    def create(self, validated_data):
        files = validated_data.pop("_upload_files")
        validated_data["video"] = files[0]
        validated_data["creator"] = self.context["request"].user
        video_post = Video.objects.create(**validated_data)
        for order, f in enumerate(files[1:], start=1):
            if hasattr(f, "seek"):
                f.seek(0)
            VideoMedia.objects.create(video_post=video_post, file=f, sort_order=order)
        return video_post

    def update(self, instance, validated_data):
        files = validated_data.pop("_upload_files", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if files:
            instance.video = files[0]
            instance.save()
            VideoMedia.objects.filter(video_post=instance).delete()
            for order, f in enumerate(files[1:], start=1):
                if hasattr(f, "seek"):
                    f.seek(0)
                VideoMedia.objects.create(video_post=instance, file=f, sort_order=order)
        else:
            instance.save()
        return instance
