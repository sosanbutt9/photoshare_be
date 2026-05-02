from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "photo", "author", "created_at")
    list_filter = ("created_at",)
    search_fields = ("body", "author__username", "author__email")
    raw_id_fields = ("photo", "author")
    readonly_fields = ("created_at", "updated_at")
