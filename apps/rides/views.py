"""ViewSets for the rides bounded context."""
from apps.common.viewsets import AdminModelViewSet
from apps.rides.filters import RideFilter
from apps.rides.models import Ride, RideEvent
from apps.rides.selectors import build_ride_list_queryset
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
        params = RideListQuerySerializer(data=self.request.query_params)
        params.is_valid(raise_exception=True)
        return build_ride_list_queryset(params.validated_data)

    def get_serializer_class(self):
        if self.action == "list":
            return RideListSerializer
        return super().get_serializer_class()


class RideEventViewSet(AdminModelViewSet):
    queryset = RideEvent.objects.all().order_by("id_ride_event")
    serializer_class = RideEventSerializer
