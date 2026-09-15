from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdmin, IsStudent, IsSupervisor
from apps.cohorts.models import Cohort
from apps.placements.models import Placement
from apps.placements.serializers import PlacementSerializer
from apps.reports.models import WeeklyReport
from apps.reports.serializers import WeeklyReportSerializer
from apps.students.models import StudentProfile
from apps.students.serializers import StudentSummarySerializer
from apps.supervisors.models import SupervisorProfile
from apps.tracks.models import Track

from .services import (
    active_placements_with_reports,
    expected_week_numbers,
    overdue_week_numbers,
    placement_progress_percentage,
)


class StudentDashboardView(APIView):
    permission_classes = [IsStudent]

    @extend_schema(responses={200: dict})
    def get(self, request):
        profile = get_object_or_404(
            StudentProfile.objects.select_related("user"), user=request.user
        )
        placement = (
            Placement.objects.filter(student=profile)
            .select_related("student__user", "supervisor__user", "track", "cohort", "created_by")
            .prefetch_related("reports")
            .order_by("status", "-start_date")
            .first()
        )
        if not placement:
            return Response(
                {
                    "profile": StudentSummarySerializer(profile).data,
                    "current_placement": None,
                    "total_expected_reports": 0,
                    "total_submitted_reports": 0,
                    "total_reviewed_reports": 0,
                    "pending_reports": 0,
                    "overdue_weeks": [],
                    "latest_supervisor_feedback": None,
                    "placement_progress_percentage": 0.0,
                }
            )

        reports = list(placement.reports.all())
        submitted = [
            report
            for report in reports
            if report.status in {WeeklyReport.Status.SUBMITTED, WeeklyReport.Status.REVIEWED}
        ]
        reviewed = [report for report in reports if report.status == WeeklyReport.Status.REVIEWED]
        latest_feedback_report = max(
            (report for report in reviewed if report.supervisor_feedback),
            key=lambda report: report.reviewed_at,
            default=None,
        )
        return Response(
            {
                "profile": StudentSummarySerializer(profile).data,
                "current_placement": PlacementSerializer(placement).data,
                "total_expected_reports": placement.total_expected_reports,
                "total_submitted_reports": len(submitted),
                "total_reviewed_reports": len(reviewed),
                "pending_reports": len(submitted) - len(reviewed),
                "overdue_weeks": overdue_week_numbers(placement),
                "latest_supervisor_feedback": (
                    latest_feedback_report.supervisor_feedback if latest_feedback_report else None
                ),
                "placement_progress_percentage": placement_progress_percentage(placement),
            }
        )


class SupervisorDashboardView(APIView):
    permission_classes = [IsSupervisor]

    @extend_schema(responses={200: dict})
    def get(self, request):
        profile = get_object_or_404(SupervisorProfile, user=request.user)
        placements = Placement.objects.filter(supervisor=profile)
        report_queryset = WeeklyReport.objects.filter(placement__supervisor=profile)
        recent = report_queryset.filter(
            status__in=[WeeklyReport.Status.SUBMITTED, WeeklyReport.Status.REVIEWED]
        ).select_related("placement__student__user", "placement__supervisor__user", "reviewed_by")[
            :10
        ]
        counts = report_queryset.aggregate(
            pending=Count("id", filter=Q(status=WeeklyReport.Status.SUBMITTED)),
            reviewed=Count("id", filter=Q(status=WeeklyReport.Status.REVIEWED)),
        )
        return Response(
            {
                "total_assigned_students": placements.values("student_id").distinct().count(),
                "active_placements": placements.filter(status=Placement.Status.ACTIVE).count(),
                "submitted_reports_awaiting_review": counts["pending"],
                "reviewed_reports": counts["reviewed"],
                "recent_submissions": WeeklyReportSerializer(recent, many=True).data,
            }
        )


class AdminDashboardView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(responses={200: dict})
    def get(self, request):
        report_counts = WeeklyReport.objects.aggregate(
            total=Count("id"),
            pending=Count("id", filter=Q(status=WeeklyReport.Status.SUBMITTED)),
            reviewed=Count("id", filter=Q(status=WeeklyReport.Status.REVIEWED)),
        )
        progress = []
        overdue_students = []
        for placement in active_placements_with_reports():
            expected = expected_week_numbers(placement)
            overdue = overdue_week_numbers(placement)
            submitted_expected = len(expected) - len(overdue)
            item = {
                "student_id": str(placement.student_id),
                "student_name": placement.student.user.full_name,
                "registration_number": placement.student.registration_number,
                "placement_id": str(placement.id),
                "expected_reports_to_date": len(expected),
                "submitted_reports_to_date": submitted_expected,
                "overdue_weeks": overdue,
                "submission_percentage": (
                    round(submitted_expected / len(expected) * 100, 2) if expected else 100.0
                ),
            }
            progress.append(item)
            if overdue:
                overdue_students.append(item)

        placement_counts = Placement.objects.aggregate(
            total=Count("id"),
            active=Count("id", filter=Q(status=Placement.Status.ACTIVE)),
            completed=Count("id", filter=Q(status=Placement.Status.COMPLETED)),
        )
        return Response(
            {
                "total_students": StudentProfile.objects.count(),
                "total_supervisors": SupervisorProfile.objects.count(),
                "total_cohorts": Cohort.objects.count(),
                "total_tracks": Track.objects.count(),
                "total_placements": placement_counts["total"],
                "active_placements": placement_counts["active"],
                "completed_placements": placement_counts["completed"],
                "total_reports": report_counts["total"],
                "pending_reviews": report_counts["pending"],
                "reviewed_reports": report_counts["reviewed"],
                "students_with_overdue_reports": overdue_students,
                "submission_progress_per_student": progress,
            }
        )
