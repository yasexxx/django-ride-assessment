"""ViewSets for the rides bounded context."""
from apps.common.viewsets import AdminModelViewSet
from apps.rides.models import Ride, RideEvent
from apps.rides.selectors import list_rides
from apps.rides.serializers import (
    RideEventSerializer,
    RideListSerializer,
    RideSerializer,
)


class RideViewSet(AdminModelViewSet):
    queryset = Ride.objects.all().order_by("id_ride")
    serializer_class = RideSerializer

    def get_queryset(self):
        # The list action uses the performance-tuned selector (select_related +
        # filtered Prefetch)
        if self.action == "list":
            return list_rides()
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == "list":
            return RideListSerializer
        return super().get_serializer_class()


class RideEventViewSet(AdminModelViewSet):
    queryset = RideEvent.objects.all().order_by("id_ride_event")
    serializer_class = RideEventSerializer
