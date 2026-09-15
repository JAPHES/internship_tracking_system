import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_health_check_is_public():
    response = APIClient().get(reverse("health"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"status": "ok", "service": "Internship Tracking System"}
