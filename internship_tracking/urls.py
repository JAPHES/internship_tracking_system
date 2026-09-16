from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="swagger-ui", permanent=False), name="home"),
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
