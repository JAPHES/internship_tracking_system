from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.permissions import IsStudent, IsSupervisor

from .filters import WeeklyReportFilter
from .models import WeeklyReport
from .serializers import ReviewReportSerializer, WeeklyReportSerializer
from .services import review_report, submit_report


class WeeklyReportViewSet(viewsets.ModelViewSet):
    serializer_class = WeeklyReportSerializer
    filterset_class = WeeklyReportFilter
    search_fields = [
        "placement__student__registration_number",
        "placement__student__user__first_name",
        "placement__student__user__last_name",
        "activities_completed",
        "skills_learned",
    ]
    ordering_fields = ["week_number", "week_start_date", "submitted_at", "reviewed_at"]
    ordering = ["-week_start_date"]

    def get_queryset(self):
        queryset = WeeklyReport.objects.select_related(
            "placement__student__user",
            "placement__supervisor__user",
            "placement__track",
            "placement__cohort",
            "reviewed_by",
        )
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.STUDENT:
            return queryset.filter(placement__student__user=user)
        if user.role == User.Role.SUPERVISOR:
            return queryset.filter(placement__supervisor__user=user)
        return queryset.none()

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "submit"}:
            return [IsStudent()]
        if self.action == "review":
            return [IsSupervisor()]
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        if serializer.instance.placement.student.user_id != self.request.user.id:
            raise PermissionDenied("Students can only edit their own reports.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role == User.Role.ADMIN:
            instance.delete()
            return
        if instance.placement.student.user_id != user.id:
            raise PermissionDenied("Students can only delete their own reports.")
        if instance.status != WeeklyReport.Status.DRAFT:
            raise ValidationError("Only draft reports can be deleted.")
        instance.delete()

    @extend_schema(request=None, responses=WeeklyReportSerializer)
    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        scoped_report = self.get_object()
        report = submit_report(report_id=scoped_report.pk, user=request.user)
        return Response(self.get_serializer(report).data)

    @extend_schema(request=ReviewReportSerializer, responses=WeeklyReportSerializer)
    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        scoped_report = self.get_object()
        input_serializer = ReviewReportSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        report = review_report(
            report_id=scoped_report.pk,
            user=request.user,
            feedback=input_serializer.validated_data["supervisor_feedback"],
        )
        return Response(self.get_serializer(report).data, status=status.HTTP_200_OK)
