from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin

from .filters import PlacementFilter
from .models import Placement
from .serializers import PlacementSerializer


class PlacementViewSet(viewsets.ModelViewSet):
    serializer_class = PlacementSerializer
    filterset_class = PlacementFilter
    search_fields = [
        "student__registration_number",
        "student__user__first_name",
        "student__user__last_name",
        "supervisor__user__first_name",
        "supervisor__user__last_name",
        "track__name",
        "cohort__name",
    ]
    ordering_fields = ["start_date", "end_date", "created_at", "status"]
    ordering = ["-start_date"]

    def get_queryset(self):
        queryset = Placement.objects.select_related(
            "student__user", "supervisor__user", "track", "cohort", "created_by"
        )
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.STUDENT:
            return queryset.filter(student__user=user)
        if user.role == User.Role.SUPERVISOR:
            return queryset.filter(supervisor__user=user)
        return queryset.none()

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @extend_schema(responses=PlacementSerializer)
    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        if request.user.role != User.Role.STUDENT:
            self.permission_denied(request, message="Student access is required.")
        queryset = self.get_queryset()
        placement = queryset.exclude(status=Placement.Status.COMPLETED).first()
        if placement is None:
            placement = get_object_or_404(queryset.order_by("-start_date"))
        return Response(self.get_serializer(placement).data)
