from rest_framework import viewsets

from apps.accounts.permissions import IsAdminOrReadOnly

from .filters import CohortFilter
from .models import Cohort
from .serializers import CohortSerializer


class CohortViewSet(viewsets.ModelViewSet):
    queryset = Cohort.objects.all()
    serializer_class = CohortSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = CohortFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "start_date", "end_date", "created_at"]
    ordering = ["-start_date", "name"]
