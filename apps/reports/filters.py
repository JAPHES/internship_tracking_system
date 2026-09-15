from django_filters import rest_framework as filters

from .models import WeeklyReport


class WeeklyReportFilter(filters.FilterSet):
    submitted_after = filters.IsoDateTimeFilter(field_name="submitted_at", lookup_expr="gte")
    submitted_before = filters.IsoDateTimeFilter(field_name="submitted_at", lookup_expr="lte")

    class Meta:
        model = WeeklyReport
        fields = ["placement", "week_number", "status", "submitted_after", "submitted_before"]
