from django.contrib import admin

from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ["registration_number", "user", "programme", "department"]
    list_filter = ["programme", "department"]
    search_fields = ["registration_number", "user__email", "user__first_name", "user__last_name"]
    list_select_related = ["user"]
