import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.students.models import StudentProfile
from tests.factories import AdminFactory, UserFactory

User = get_user_model()
pytestmark = pytest.mark.django_db


def test_user_manager_creates_email_user():
    user = User.objects.create_user(
        email="MixedCase@Example.COM",
        password="StrongPass123!",
        first_name="Amina",
        last_name="Otieno",
        role=User.Role.STUDENT,
    )

    assert user.email == "mixedcase@example.com"
    assert user.check_password("StrongPass123!")
    assert user.pk is not None


def test_create_superuser_enforces_admin_role():
    user = User.objects.create_superuser(
        email="admin@example.com",
        password="StrongPass123!",
        first_name="System",
        last_name="Admin",
    )

    assert user.role == User.Role.ADMIN
    assert user.is_staff is True
    assert user.is_superuser is True


def test_student_registration_creates_profile_atomically():
    response = APIClient().post(
        reverse("student-register"),
        {
            "email": "student@example.com",
            "password": "StrongPass123!",
            "first_name": "Jane",
            "last_name": "Doe",
            "registration_number": "S001",
            "programme": "BSc Computer Science",
            "department": "Computing",
            "phone_number": "+254700000001",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    user = User.objects.get(email="student@example.com")
    assert user.role == User.Role.STUDENT
    assert StudentProfile.objects.filter(user=user, registration_number="S001").exists()


def test_jwt_login_and_current_user_endpoint():
    user = UserFactory(email="login@example.com")
    client = APIClient()

    login = client.post(
        reverse("token-obtain-pair"),
        {"email": user.email, "password": "StrongPass123!"},
        format="json",
    )

    assert login.status_code == status.HTTP_200_OK
    assert {"access", "refresh", "user"}.issubset(login.data)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    me = client.get(reverse("current-user"))
    assert me.status_code == status.HTTP_200_OK
    assert me.data["email"] == user.email


def test_only_admin_can_list_accounts():
    student = UserFactory()
    client = APIClient()
    client.force_authenticate(student)
    denied = client.get(reverse("user-list"))
    assert denied.status_code == status.HTTP_403_FORBIDDEN

    client.force_authenticate(AdminFactory())
    allowed = client.get(reverse("user-list"))
    assert allowed.status_code == status.HTTP_200_OK
