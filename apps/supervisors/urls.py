from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MyAssignedStudentsView, MySupervisorProfileView, SupervisorProfileViewSet

router = DefaultRouter()
router.register("", SupervisorProfileViewSet, basename="supervisor")

urlpatterns = [
    path("me/students/", MyAssignedStudentsView.as_view(), name="supervisor-students"),
    path("me/", MySupervisorProfileView.as_view(), name="supervisor-me"),
    path("", include(router.urls)),
]
