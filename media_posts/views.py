from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from comments.serializers import CommentCreateSerializer, CommentSerializer
from common.filters import QueryParamSearchFilter
from common.pagination import StandardResultsPagination
from common.permissions import IsCreatorOwnerOrAdmin, IsCreatorUser

from ratings.serializers import RatingSerializer
from ratings.services import set_photo_rating

from .filters import PhotoFilter
from .models import Photo
from .serializers import (
    PhotoDetailSerializer,
    PhotoListSerializer,
    PhotoRateSerializer,
    PhotoWriteSerializer,
)
from .services import increment_photo_view_count


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.select_related("creator").all()
    pagination_class = StandardResultsPagination
    filter_backends = (
        DjangoFilterBackend,
        QueryParamSearchFilter,
        OrderingFilter,
    )
    filterset_class = PhotoFilter
    search_fields = (
        "title",
        "caption",
        "location",
        "people_present",
        "creator__username",
        "creator__full_name",
    )
    ordering_fields = ("created_at", "updated_at", "view_count", "title")
    ordering = ("-created_at",)
    lookup_value_regex = r"[0-9]+"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(
            average_rating=Avg("ratings__score"),
            ratings_count=Count("ratings", distinct=True),
        ).prefetch_related("media_items")

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return PhotoWriteSerializer
        if self.action == "retrieve":
            return PhotoDetailSerializer
        return PhotoListSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve", "search"):
            return [permissions.AllowAny()]
        if self.action == "comments":
            if self.request.method == "POST":
                return [permissions.IsAuthenticated()]
            return [permissions.AllowAny()]
        if self.action in ("ratings",):
            return [permissions.AllowAny()]
        if self.action in ("rate",):
            return [permissions.IsAuthenticated()]
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsCreatorUser()]
        if self.action in ("update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsCreatorOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        increment_photo_view_count(instance)
        serializer = self.get_serializer(instance)
        return Response({"success": True, "photo": serializer.data})

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if isinstance(response.data, dict) and "results" in response.data:
            return Response(
                {
                    "success": True,
                    "count": response.data.get("count"),
                    "next": response.data.get("next"),
                    "previous": response.data.get("previous"),
                    "results": response.data["results"],
                }
            )
        return Response({"success": True, "results": response.data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        out = PhotoDetailSerializer(
            self.get_queryset().get(pk=serializer.instance.pk),
            context={"request": request},
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"success": True, "photo": out.data},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        out = PhotoDetailSerializer(
            self.get_queryset().get(pk=instance.pk),
            context={"request": request},
        )
        return Response({"success": True, "photo": out.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "detail": "Photo deleted."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        photo = self.get_object()
        if request.method == "GET":
            qs = photo.comments.select_related("author").all()
            page = self.paginate_queryset(qs)
            ser = CommentSerializer(page if page is not None else qs, many=True)
            if page is not None:
                paginated = self.get_paginated_response(ser.data)
                paginated.data["success"] = True
                return paginated
            return Response({"success": True, "results": ser.data})
        ser_in = CommentCreateSerializer(
            data=request.data,
            context={"request": request, "photo": photo},
        )
        ser_in.is_valid(raise_exception=True)
        comment = ser_in.save()
        return Response(
            {"success": True, "comment": CommentSerializer(comment).data},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="rate")
    def rate(self, request, pk=None):
        photo = self.get_object()
        ser = PhotoRateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        score = ser.validated_data["score"]
        rating, created = set_photo_rating(user=request.user, photo=photo, score=score)
        body = RatingSerializer(rating).data
        code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(
            {
                "success": True,
                "created": created,
                "rating": body,
            },
            status=code,
        )

    @action(detail=True, methods=["get"], url_path="ratings")
    def ratings(self, request, pk=None):
        photo = self.get_object()
        qs = photo.ratings.select_related("user").all()
        page = self.paginate_queryset(qs)
        ser = RatingSerializer(page if page is not None else qs, many=True)
        if page is not None:
            paginated = self.get_paginated_response(ser.data)
            paginated.data["success"] = True
            return paginated
        return Response({"success": True, "results": ser.data})
