from datetime import date, timedelta

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.factories import (
    AdminFactory,
    CohortFactory,
    PlacementFactory,
    StudentProfileFactory,
    SupervisorProfileFactory,
    TrackFactory,
)

pytestmark = pytest.mark.django_db


def placement_payload(student, supervisor, track, cohort, **overrides):
    payload = {
        "student": str(student.pk),
        "supervisor": str(supervisor.pk),
        "track": str(track.pk),
        "cohort": str(cohort.pk),
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=70)),
        "status": "ACTIVE",
    }
    payload.update(overrides)
    return payload


def test_placement_rejects_invalid_date_range():
    admin = AdminFactory()
    student = StudentProfileFactory()
    supervisor = SupervisorProfileFactory()
    client = APIClient()
    client.force_authenticate(admin)

    response = client.post(
        reverse("placement-list"),
        placement_payload(
            student,
            supervisor,
            TrackFactory(),
            CohortFactory(),
            start_date="2026-08-10",
            end_date="2026-08-01",
        ),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_duplicate_current_placement_is_rejected():
    existing = PlacementFactory()
    client = APIClient()
    client.force_authenticate(existing.created_by)

    response = client.post(
        reverse("placement-list"),
        placement_payload(
            existing.student,
            SupervisorProfileFactory(),
            TrackFactory(),
            CohortFactory(),
        ),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_placement_visibility_is_role_scoped():
    first = PlacementFactory()
    second = PlacementFactory()
    client = APIClient()

    client.force_authenticate(first.student.user)
    student_response = client.get(reverse("placement-list"))
    assert student_response.status_code == status.HTTP_200_OK
    assert student_response.data["count"] == 1

    client.force_authenticate(first.supervisor.user)
    supervisor_response = client.get(reverse("placement-list"))
    assert supervisor_response.status_code == status.HTTP_200_OK
    assert supervisor_response.data["count"] == 1
    assert str(second.pk) not in str(supervisor_response.data)


def test_only_admin_can_create_placement():
    student = StudentProfileFactory()
    client = APIClient()
    client.force_authenticate(student.user)
    response = client.post(reverse("placement-list"), {}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN
