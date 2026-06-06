"""Rides API routes."""
from config.router import router

from apps.rides.views import RideEventViewSet, RideViewSet

app_name = "rides"

router.register("rides", RideViewSet, basename="ride")
router.register("ride-events", RideEventViewSet, basename="ride-event")

urlpatterns = router.urls
