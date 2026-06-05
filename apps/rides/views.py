"""ViewSets for the rides bounded context."""
from apps.common.viewsets import AdminModelViewSet
from apps.rides.models import Ride, RideEvent
from apps.rides.serializers import RideEventSerializer, RideSerializer


class RideViewSet(AdminModelViewSet):
    queryset = Ride.objects.all().order_by("id_ride")
    serializer_class = RideSerializer


class RideEventViewSet(AdminModelViewSet):
    queryset = RideEvent.objects.all().order_by("id_ride_event")
    serializer_class = RideEventSerializer
