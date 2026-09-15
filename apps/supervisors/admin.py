from django.contrib import admin

from .models import SupervisorProfile


@admin.register(SupervisorProfile)
class SupervisorProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "staff_number", "department"]
    list_filter = ["department"]
    search_fields = ["staff_number", "user__email", "user__first_name", "user__last_name"]
    list_select_related = ["user"]
