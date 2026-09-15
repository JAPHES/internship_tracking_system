from rest_framework.routers import DefaultRouter

from .views import PlacementViewSet

router = DefaultRouter()
router.register("", PlacementViewSet, basename="placement")
urlpatterns = router.urls
