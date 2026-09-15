from rest_framework.routers import DefaultRouter

from .views import CohortViewSet

router = DefaultRouter()
router.register("", CohortViewSet, basename="cohort")
urlpatterns = router.urls
