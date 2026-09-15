from django_filters import rest_framework as filters

from .models import SupervisorProfile


class SupervisorProfileFilter(filters.FilterSet):
    class Meta:
        model = SupervisorProfile
        fields = {"department": ["exact", "icontains"]}
