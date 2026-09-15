from django.contrib import admin

from .models import WeeklyReport


@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ["placement", "week_number", "status", "submitted_at", "reviewed_at"]
    list_filter = ["status", "week_start_date", "placement__cohort"]
    search_fields = [
        "placement__student__registration_number",
        "placement__student__user__email",
        "activities_completed",
    ]
    list_select_related = ["placement__student__user", "placement__cohort", "reviewed_by"]
