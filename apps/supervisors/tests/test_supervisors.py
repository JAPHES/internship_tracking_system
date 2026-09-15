import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.factories import PlacementFactory, StudentProfileFactory, SupervisorProfileFactory

pytestmark = pytest.mark.django_db


def test_supervisor_can_update_own_profile():
    profile = SupervisorProfileFactory()
    client = APIClient()
    client.force_authenticate(profile.user)

    response = client.patch(
        reverse("supervisor-me"), {"phone_number": "+254744000000"}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    profile.refresh_from_db()
    assert profile.phone_number == "+254744000000"


def test_supervisor_assigned_student_list_excludes_other_students():
    placement = PlacementFactory()
    other_student = StudentProfileFactory()
    client = APIClient()
    client.force_authenticate(placement.supervisor.user)

    response = client.get(reverse("supervisor-students"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == str(placement.student_id)
    assert str(other_student.pk) not in str(response.data)


def test_student_cannot_access_supervisor_self_endpoint():
    student = StudentProfileFactory()
    client = APIClient()
    client.force_authenticate(student.user)

    response = client.get(reverse("supervisor-me"))

    assert response.status_code == status.HTTP_403_FORBIDDEN
