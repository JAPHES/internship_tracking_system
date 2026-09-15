from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MyStudentProfileView, StudentProfileViewSet

router = DefaultRouter()
router.register("", StudentProfileViewSet, basename="student")

urlpatterns = [
    path("me/", MyStudentProfileView.as_view(), name="student-me"),
    path("", include(router.urls)),
]
