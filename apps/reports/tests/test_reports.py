from datetime import timedelta

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.reports.models import WeeklyReport
from tests.factories import PlacementFactory, SupervisorProfileFactory, WeeklyReportFactory

pytestmark = pytest.mark.django_db


def report_payload(placement, week_number=1):
    week_start = placement.start_date + timedelta(days=7 * (week_number - 1))
    return {
        "placement": str(placement.pk),
        "week_number": week_number,
        "week_start_date": str(week_start),
        "week_end_date": str(min(week_start + timedelta(days=6), placement.end_date)),
        "activities_completed": "Built the reporting endpoint.",
        "skills_learned": "Serializer validation",
        "challenges_faced": "Test setup",
    }


def test_student_creates_and_submits_weekly_report():
    placement = PlacementFactory()
    client = APIClient()
    client.force_authenticate(placement.student.user)

    created = client.post(reverse("report-list"), report_payload(placement), format="json")
    assert created.status_code == status.HTTP_201_CREATED
    assert created.data["status"] == WeeklyReport.Status.DRAFT

    submitted = client.post(reverse("report-submit", args=[created.data["id"]]), format="json")
    assert submitted.status_code == status.HTTP_200_OK
    assert submitted.data["status"] == WeeklyReport.Status.SUBMITTED
    assert submitted.data["submitted_at"] is not None


def test_student_cannot_create_report_for_another_students_placement():
    own_placement = PlacementFactory()
    other_placement = PlacementFactory()
    client = APIClient()
    client.force_authenticate(own_placement.student.user)

    response = client.post(reverse("report-list"), report_payload(other_placement), format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_assigned_supervisor_can_review_submitted_report():
    report = WeeklyReportFactory(status=WeeklyReport.Status.SUBMITTED)
    client = APIClient()
    client.force_authenticate(report.placement.supervisor.user)

    response = client.post(
        reverse("report-review", args=[report.pk]),
        {"supervisor_feedback": "Good progress."},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    report.refresh_from_db()
    assert report.status == WeeklyReport.Status.REVIEWED
    assert report.reviewed_by == report.placement.supervisor.user


def test_unassigned_supervisor_cannot_review_report():
    report = WeeklyReportFactory(status=WeeklyReport.Status.SUBMITTED)
    stranger = SupervisorProfileFactory()
    client = APIClient()
    client.force_authenticate(stranger.user)

    response = client.post(
        reverse("report-review", args=[report.pk]),
        {"supervisor_feedback": "Should not work."},
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_reviewed_report_can_be_edited_and_resubmitted_with_feedback_retained():
    report = WeeklyReportFactory(
        status=WeeklyReport.Status.REVIEWED,
        supervisor_feedback="Please add detail.",
    )
    report.reviewed_by = report.placement.supervisor.user
    report.save(update_fields=["reviewed_by"])
    client = APIClient()
    client.force_authenticate(report.placement.student.user)

    edited = client.patch(
        reverse("report-detail", args=[report.pk]),
        {"activities_completed": "Added the requested implementation detail."},
        format="json",
    )
    assert edited.status_code == status.HTTP_200_OK

    submitted = client.post(reverse("report-submit", args=[report.pk]), format="json")
    assert submitted.status_code == status.HTTP_200_OK
    assert submitted.data["status"] == WeeklyReport.Status.SUBMITTED
    assert submitted.data["supervisor_feedback"] == "Please add detail."
    assert submitted.data["reviewed_by"] is None
