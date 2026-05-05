from django.contrib import admin

from .models import Photo, PhotoMedia, Video, VideoMedia


class PhotoMediaInline(admin.TabularInline):
    model = PhotoMedia
    extra = 0


class VideoMediaInline(admin.TabularInline):
    model = VideoMedia
    extra = 0


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "view_count", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "caption", "location", "people_present", "creator__username", "creator__email")
    readonly_fields = ("view_count", "created_at", "updated_at")
    raw_id_fields = ("creator",)
    inlines = (PhotoMediaInline,)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "view_count", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "caption", "location", "people_present", "creator__username", "creator__email")
    readonly_fields = ("view_count", "created_at", "updated_at")
    raw_id_fields = ("creator",)
    inlines = (VideoMediaInline,)
