from django_filters import rest_framework as filters

from .models import Cohort


class CohortFilter(filters.FilterSet):
    starts_after = filters.DateFilter(field_name="start_date", lookup_expr="gte")
    ends_before = filters.DateFilter(field_name="end_date", lookup_expr="lte")

    class Meta:
        model = Cohort
        fields = ["is_active", "starts_after", "ends_before"]
