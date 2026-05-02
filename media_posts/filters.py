import django_filters

from .models import Photo


class PhotoFilter(django_filters.FilterSet):
    creator = django_filters.NumberFilter(field_name="creator_id")
    title = django_filters.CharFilter(lookup_expr="icontains")
    caption = django_filters.CharFilter(lookup_expr="icontains")
    location = django_filters.CharFilter(lookup_expr="icontains")
    people_present = django_filters.CharFilter(lookup_expr="icontains")
    creator__username = django_filters.CharFilter(lookup_expr="icontains")
    creator__full_name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Photo
        fields = (
            "creator",
            "title",
            "caption",
            "location",
            "people_present",
            "creator__username",
            "creator__full_name",
        )
