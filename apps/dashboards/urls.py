from django.urls import path

from .views import AdminDashboardView, StudentDashboardView, SupervisorDashboardView

urlpatterns = [
    path("student/", StudentDashboardView.as_view(), name="student-dashboard"),
    path("supervisor/", SupervisorDashboardView.as_view(), name="supervisor-dashboard"),
    path("admin/", AdminDashboardView.as_view(), name="admin-dashboard"),
]
