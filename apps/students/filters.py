from django_filters import rest_framework as filters

from .models import StudentProfile


class StudentProfileFilter(filters.FilterSet):
    class Meta:
        model = StudentProfile
        fields = {"programme": ["exact", "icontains"], "department": ["exact", "icontains"]}
