from django.contrib import admin

from .models import Placement


@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    list_display = ["student", "supervisor", "track", "cohort", "status", "start_date", "end_date"]
    list_filter = ["status", "cohort", "track", "start_date"]
    search_fields = [
        "student__registration_number",
        "student__user__email",
        "supervisor__user__email",
    ]
    list_select_related = ["student__user", "supervisor__user", "track", "cohort"]
