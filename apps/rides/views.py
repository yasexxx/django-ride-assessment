"""ViewSets for the rides bounded context."""
from django.contrib.gis.geos import Point

from apps.common.constants import WGS84_SRID
from apps.common.viewsets import AdminModelViewSet
from apps.rides.constants import RideOrdering
from apps.rides.filters import RideFilter
from apps.rides.models import Ride, RideEvent
from apps.rides.selectors import list_rides, order_rides
from apps.rides.serializers import (
    RideEventSerializer,
    RideListQuerySerializer,
    RideListSerializer,
    RideSerializer,
)


class RideViewSet(AdminModelViewSet):
    queryset = Ride.objects.all().order_by("id_ride")
    serializer_class = RideSerializer
    filterset_class = RideFilter

    def get_queryset(self):
        if self.action != "list":
            return super().get_queryset()

        # The list action uses the performance-tuned selector (select_related +
        # filtered Prefetch) plus validated sorting.
        params = RideListQuerySerializer(data=self.request.query_params)
        params.is_valid(raise_exception=True)
        data = params.validated_data

        pickup_point = None
        if data.get("ordering") == RideOrdering.DISTANCE:
            pickup_point = Point(
                data["pickup_lng"], data["pickup_lat"], srid=WGS84_SRID
            )
        return order_rides(
            list_rides(), ordering=data.get("ordering"), pickup_point=pickup_point
        )

    def get_serializer_class(self):
        if self.action == "list":
            return RideListSerializer
        return super().get_serializer_class()


class RideEventViewSet(AdminModelViewSet):
    queryset = RideEvent.objects.all().order_by("id_ride_event")
    serializer_class = RideEventSerializer
