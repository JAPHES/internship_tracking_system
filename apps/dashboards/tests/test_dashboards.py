from datetime import date, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.reports.models import WeeklyReport
from tests.factories import AdminFactory, PlacementFactory, WeeklyReportFactory

pytestmark = pytest.mark.django_db


def test_student_dashboard_calculates_reports_and_overdue_weeks():
    placement = PlacementFactory(
        start_date=date.today() - timedelta(days=21),
        end_date=date.today() + timedelta(days=49),
    )
    WeeklyReportFactory(
        placement=placement,
        week_number=1,
        week_start_date=placement.start_date,
        week_end_date=placement.start_date + timedelta(days=6),
        status=WeeklyReport.Status.REVIEWED,
        supervisor_feedback="On track.",
        reviewed_at=timezone.now() - timedelta(days=10),
    )
    client = APIClient()
    client.force_authenticate(placement.student.user)

    response = client.get(reverse("student-dashboard"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_reviewed_reports"] == 1
    assert response.data["latest_supervisor_feedback"] == "On track."
    assert response.data["overdue_weeks"] == [2, 3]
    assert 0 < response.data["placement_progress_percentage"] < 100


def test_supervisor_dashboard_only_counts_assigned_reports():
    assigned = PlacementFactory()
    WeeklyReportFactory(placement=assigned, status=WeeklyReport.Status.SUBMITTED)
    WeeklyReportFactory(status=WeeklyReport.Status.SUBMITTED)
    client = APIClient()
    client.force_authenticate(assigned.supervisor.user)

    response = client.get(reverse("supervisor-dashboard"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_assigned_students"] == 1
    assert response.data["submitted_reports_awaiting_review"] == 1


def test_admin_dashboard_identifies_overdue_student():
    placement = PlacementFactory(
        start_date=date.today() - timedelta(days=14),
        end_date=date.today() + timedelta(days=56),
    )
    client = APIClient()
    client.force_authenticate(AdminFactory())

    response = client.get(reverse("admin-dashboard"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["active_placements"] == 1
    assert response.data["students_with_overdue_reports"][0]["student_id"] == str(
        placement.student_id
    )
