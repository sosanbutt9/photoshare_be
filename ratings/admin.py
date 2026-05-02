from django.contrib import admin

from .models import Rating


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("id", "photo", "user", "score", "updated_at")
    list_filter = ("score", "created_at")
    search_fields = ("user__username", "user__email", "photo__title")
    raw_id_fields = ("photo", "user")
    readonly_fields = ("created_at", "updated_at")
