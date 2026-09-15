from django_filters import rest_framework as filters

from .models import Track


class TrackFilter(filters.FilterSet):
    class Meta:
        model = Track
        fields = ["is_active"]
