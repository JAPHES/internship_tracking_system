from rest_framework.routers import DefaultRouter

from .views import TrackViewSet

router = DefaultRouter()
router.register("", TrackViewSet, basename="track")
urlpatterns = router.urls
