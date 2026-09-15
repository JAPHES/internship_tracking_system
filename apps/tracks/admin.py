from django.contrib import admin

from .models import Track


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]
