"""Rides API routes."""
from rest_framework.routers import DefaultRouter

from apps.rides.views import RideEventViewSet, RideViewSet

app_name = "rides"

router = DefaultRouter()
router.register("rides", RideViewSet, basename="ride")
router.register("ride-events", RideEventViewSet, basename="ride-event")

urlpatterns = router.urls
