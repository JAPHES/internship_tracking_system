import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.factories import AdminFactory, StudentProfileFactory

pytestmark = pytest.mark.django_db


def test_student_can_read_and_patch_own_profile():
    profile = StudentProfileFactory()
    client = APIClient()
    client.force_authenticate(profile.user)

    response = client.patch(reverse("student-me"), {"phone_number": "+254722123456"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    profile.refresh_from_db()
    assert profile.phone_number == "+254722123456"


def test_student_cannot_retrieve_another_profile():
    profile = StudentProfileFactory()
    other = StudentProfileFactory()
    client = APIClient()
    client.force_authenticate(profile.user)

    response = client.get(reverse("student-detail", args=[other.pk]))

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_admin_can_create_student_profile_and_account():
    client = APIClient()
    client.force_authenticate(AdminFactory())
    response = client.post(
        reverse("student-list"),
        {
            "email": "newstudent@example.com",
            "password": "StrongPass123!",
            "first_name": "New",
            "last_name": "Student",
            "registration_number": "NEW-001",
            "programme": "Data Science",
            "department": "Computing",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["registration_number"] == "NEW-001"
