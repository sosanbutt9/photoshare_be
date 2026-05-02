from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAdminUserRole

from .services import platform_summary, recent_photos, recent_users


class AdminStatsView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        summary = platform_summary()
        return Response(
            {
                "success": True,
                "summary": summary,
                "recent_users": recent_users(10),
                "recent_photos": recent_photos(10),
            }
        )
