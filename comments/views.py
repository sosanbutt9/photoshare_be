from rest_framework import mixins, permissions, status, viewsets
from rest_framework.response import Response

from common.permissions import IsOwnerOrAdmin

from .models import Comment
from .serializers import CommentSerializer


class CommentViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Comment.objects.select_related("author", "photo").all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    lookup_value_regex = r"[0-9]+"

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"success": True, "detail": "Comment deleted."},
            status=status.HTTP_200_OK,
        )