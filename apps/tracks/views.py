from rest_framework import viewsets

from apps.accounts.permissions import IsAdminOrReadOnly

from .filters import TrackFilter
from .models import Track
from .serializers import TrackSerializer


class TrackViewSet(viewsets.ModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = TrackFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
