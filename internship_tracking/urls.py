from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("", TemplateView.as_view(template_name="frontend/home.html"), name="home"),
    path(
        "login/",
        TemplateView.as_view(template_name="frontend/login.html"),
        name="frontend-login",
    ),
    path(
        "register/",
        TemplateView.as_view(template_name="frontend/register.html"),
        name="frontend-register",
    ),
    path(
        "dashboard/",
        TemplateView.as_view(template_name="frontend/dashboard.html"),
        name="frontend-dashboard",
    ),
    path(
        "system-guide/",
        TemplateView.as_view(template_name="frontend/system_guide.html"),
        name="system-guide",
    ),
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/students/", include("apps.students.urls")),
    path("api/v1/supervisors/", include("apps.supervisors.urls")),
    path("api/v1/cohorts/", include("apps.cohorts.urls")),
    path("api/v1/tracks/", include("apps.tracks.urls")),
    path("api/v1/placements/", include("apps.placements.urls")),
    path("api/v1/reports/", include("apps.reports.urls")),
    path("api/v1/dashboard/", include("apps.dashboards.urls")),
    path("api/v1/", include("apps.common.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
