import io

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.utils.datastructures import MultiValueDict
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from media_posts.models import Photo, PhotoMedia, Video, VideoMedia
from media_posts.serializers import PhotoWriteSerializer, VideoWriteSerializer

User = get_user_model()


def _small_jpeg_bytes():
    buf = io.BytesIO()
    Image.new("RGB", (20, 20), color=(120, 40, 200)).save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


def _small_video_bytes():
    # Minimal bytes for upload tests; backend accepts file uploads via FileField.
    return b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom"


class CreatorPhotoUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.creator = User.objects.create_user(
            email="creator@example.com",
            username="creator1",
            password="creatorpass1",
            role=User.Role.CREATOR,
        )
        refresh = self.client.post(
            "/api/auth/login/",
            {"email": self.creator.email, "password": "creatorpass1"},
            format="json",
        ).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh}")

    def test_creator_can_upload_photo(self):
        upload = SimpleUploadedFile(
            "shot.jpg",
            _small_jpeg_bytes(),
            content_type="image/jpeg",
        )
        response = self.client.post(
            "/api/photos/",
            {
                "title": "Sunset",
                "caption": "Nice evening",
                "location": "Beach",
                "people_present": "Friends",
                "image": upload,
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["photo"]["title"], "Sunset")
        self.assertTrue(Photo.objects.filter(title="Sunset").exists())

    def test_creator_can_upload_carousel_post_via_files_getlist(self):
        """Multipart uploads expose repeated ``images`` keys as FILES.getlist('images')."""
        up1 = SimpleUploadedFile(
            "a.jpg",
            _small_jpeg_bytes(),
            content_type="image/jpeg",
        )
        up2 = SimpleUploadedFile(
            "b.jpg",
            _small_jpeg_bytes(),
            content_type="image/jpeg",
        )
        factory = RequestFactory()
        django_request = factory.post("/api/photos/")
        django_request.user = self.creator
        django_request.FILES = MultiValueDict()
        django_request.FILES.setlist("images", [up1, up2])

        ser = PhotoWriteSerializer(
            data={"title": "Trip", "caption": "Several frames"},
            context={"request": django_request},
        )
        self.assertTrue(ser.is_valid(), ser.errors)
        photo = ser.save()
        self.assertEqual(PhotoMedia.objects.filter(photo=photo).count(), 1)
        self.assertTrue(photo.image.name)


class ConsumerCommentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.creator = User.objects.create_user(
            email="c@example.com",
            username="c1",
            password="p1creator1",
            role=User.Role.CREATOR,
        )
        self.consumer = User.objects.create_user(
            email="cons@example.com",
            username="cons1",
            password="p1consumer1",
            role=User.Role.CONSUMER,
        )
        self.photo = Photo.objects.create(
            creator=self.creator,
            title="Photo",
            caption="",
            image=SimpleUploadedFile("x.jpg", _small_jpeg_bytes(), content_type="image/jpeg"),
        )
        access = self.client.post(
            "/api/auth/login/",
            {"email": self.consumer.email, "password": "p1consumer1"},
            format="json",
        ).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_consumer_can_comment_on_photo(self):
        response = self.client.post(
            f"/api/photos/{self.photo.pk}/comments/",
            {"body": "Great shot!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["comment"]["body"], "Great shot!")


class ConsumerRatingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.creator = User.objects.create_user(
            email="cr@example.com",
            username="cr1",
            password="pcreator11",
            role=User.Role.CREATOR,
        )
        self.consumer = User.objects.create_user(
            email="co@example.com",
            username="co1",
            password="pconsumer11",
            role=User.Role.CONSUMER,
        )
        self.photo = Photo.objects.create(
            creator=self.creator,
            title="Art",
            caption="",
            image=SimpleUploadedFile("y.jpg", _small_jpeg_bytes(), content_type="image/jpeg"),
        )
        access = self.client.post(
            "/api/auth/login/",
            {"email": self.consumer.email, "password": "pconsumer11"},
            format="json",
        ).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_consumer_can_rate_photo(self):
        response = self.client.post(
            f"/api/photos/{self.photo.pk}/rate/",
            {"score": 5},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["rating"]["score"], 5)

        again = self.client.post(
            f"/api/photos/{self.photo.pk}/rate/",
            {"score": 3},
            format="json",
        )
        self.assertEqual(again.status_code, status.HTTP_200_OK)
        self.assertFalse(again.data["created"])
        self.assertEqual(again.data["rating"]["score"], 3)


class CreatorVideoUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.creator = User.objects.create_user(
            email="video_creator@example.com",
            username="video_creator1",
            password="creatorpass2",
            role=User.Role.CREATOR,
        )
        access = self.client.post(
            "/api/auth/login/",
            {"email": self.creator.email, "password": "creatorpass2"},
            format="json",
        ).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_creator_can_upload_multiple_videos(self):
        clip1 = SimpleUploadedFile("a.mp4", _small_video_bytes(), content_type="video/mp4")
        clip2 = SimpleUploadedFile("b.mp4", _small_video_bytes(), content_type="video/mp4")
        response = self.client.post(
            "/api/videos/",
            {
                "title": "My clips",
                "caption": "Batch upload",
                "videos": [clip1, clip2],
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["video"]["title"], "My clips")
        video_post = Video.objects.get(pk=response.data["video"]["id"])
        self.assertTrue(video_post.video.name)
        self.assertEqual(VideoMedia.objects.filter(video_post=video_post).count(), 1)

    def test_creator_can_update_video_post(self):
        video_post = Video.objects.create(
            creator=self.creator,
            title="Old title",
            caption="",
            video=SimpleUploadedFile("old.mp4", _small_video_bytes(), content_type="video/mp4"),
        )
        response = self.client.patch(
            f"/api/videos/{video_post.pk}/",
            {"title": "New title", "caption": "Updated"},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["video"]["title"], "New title")

    def test_serializer_supports_repeated_videos_getlist(self):
        clip1 = SimpleUploadedFile("1.mp4", _small_video_bytes(), content_type="video/mp4")
        clip2 = SimpleUploadedFile("2.mp4", _small_video_bytes(), content_type="video/mp4")
        factory = RequestFactory()
        django_request = factory.post("/api/videos/")
        django_request.user = self.creator
        django_request.FILES = MultiValueDict()
        django_request.FILES.setlist("videos", [clip1, clip2])

        ser = VideoWriteSerializer(
            data={"title": "Batch", "caption": "Two clips"},
            context={"request": django_request},
        )
        self.assertTrue(ser.is_valid(), ser.errors)
        video_post = ser.save()
        self.assertEqual(VideoMedia.objects.filter(video_post=video_post).count(), 1)
