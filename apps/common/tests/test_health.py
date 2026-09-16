import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_health_check_is_public():
    response = APIClient().get(reverse("health"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"status": "ok", "service": "Internship Tracking System"}


def test_frontend_pages_render():
    client = APIClient()

    for route_name in (
        "home",
        "frontend-login",
        "frontend-register",
        "frontend-dashboard",
        "system-guide",
    ):
        response = client.get(reverse(route_name))

        assert response.status_code == status.HTTP_200_OK
        assert b"Internship Tracking" in response.content


def test_home_introduces_all_user_roles():
    response = APIClient().get(reverse("home"))

    assert b"Student workspace" in response.content
    assert b"Supervisor workspace" in response.content
    assert b"Administrator workspace" in response.content
