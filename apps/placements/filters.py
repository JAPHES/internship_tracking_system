from django_filters import rest_framework as filters

from .models import Placement


class PlacementFilter(filters.FilterSet):
    starts_after = filters.DateFilter(field_name="start_date", lookup_expr="gte")
    ends_before = filters.DateFilter(field_name="end_date", lookup_expr="lte")

    class Meta:
        model = Placement
        fields = [
            "student",
            "supervisor",
            "track",
            "cohort",
            "status",
            "starts_after",
            "ends_before",
        ]
