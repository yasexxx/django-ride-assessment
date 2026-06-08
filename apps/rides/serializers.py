"""
Serializers for the rides domain.

Serializer responsibilities:
- ``RideSerializer``: Write/detail representation used by create, update,
  retrieve, and delete operations.
- ``RideListSerializer``: Read-optimized representation for list endpoints,
  including nested rider/driver data and recent ride events.
- ``RideEventSerializer``: Representation of ride event records.

The list serializer relies on query optimizations performed by
``apps.rides.selectors.list_rides`` and should be used only with querysets
that provide the required related objects and prefetched attributes.
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.serializers import UserSerializer
from apps.common.constants import (
    LATITUDE_MAX,
    LATITUDE_MIN,
    LONGITUDE_MAX,
    LONGITUDE_MIN,
)
from apps.rides.constants import RideOrdering
from apps.rides.models import Ride, RideEvent
from apps.rides.services import create_ride, create_ride_event, update_ride

User = get_user_model()


class RideEventSerializer(serializers.ModelSerializer):
    """Serializes ride event records."""

    class Meta:
        model = RideEvent
        fields = ["id_ride_event", "id_ride", "description", "created_at"]
        read_only_fields = ["id_ride_event", "created_at"]

    def create(self, validated_data: dict) -> RideEvent:
        return create_ride_event(validated_data)


class RideSerializer(serializers.ModelSerializer):
    """
    Serializer used for ride creation, updates, and detail views.
    """

    class Meta:
        model = Ride
        fields = [
            "id_ride",
            "status",
            "id_rider",
            "id_driver",
            "pickup_latitude",
            "pickup_longitude",
            "dropoff_latitude",
            "dropoff_longitude",
            "pickup_time",
        ]
        read_only_fields = ["id_ride"]

    def validate_id_rider(self, user):
        """Ensure the selected user is eligible to be assigned as a rider."""
        if user.role != User.Role.RIDER:
            raise serializers.ValidationError("Must be a user with role 'rider'.")
        return user

    def validate_id_driver(self, user):
        """Ensure the selected user is eligible to be assigned as a driver."""
        if user.role != User.Role.DRIVER:
            raise serializers.ValidationError("Must be a user with role 'driver'.")
        return user

    def create(self, validated_data: dict) -> Ride:
        return create_ride(validated_data)

    def update(self, instance: Ride, validated_data: dict) -> Ride:
        return update_ride(instance, validated_data)


class RideListSerializer(serializers.ModelSerializer):
    """Read serializer for the Ride List API.

    Nests the related rider/driver (populated by the selector's
    ``select_related``) and exposes ``todays_ride_events`` (the last-24h events
    attached by the selector's filtered ``Prefetch``). Must be used with
    ``apps.rides.selectors.list_rides`` so these attributes are present without
    triggering extra queries.
    """

    id_rider = UserSerializer(read_only=True)
    id_driver = UserSerializer(read_only=True)
    todays_ride_events = RideEventSerializer(many=True, read_only=True)

    class Meta:
        model = Ride
        fields = [
            "id_ride",
            "status",
            "id_rider",
            "id_driver",
            "pickup_latitude",
            "pickup_longitude",
            "dropoff_latitude",
            "dropoff_longitude",
            "pickup_time",
            "todays_ride_events",
        ]


class RideListQuerySerializer(serializers.Serializer):
    """Validates the Ride List sorting query parameters.

    ``ordering`` selects the sort; ``pickup_lat`` / ``pickup_lng`` provide the
    reference point and are required (and bounded) only when sorting by
    distance.
    """

    ordering = serializers.ChoiceField(choices=RideOrdering.ALL, required=False)
    pickup_lat = serializers.FloatField(
        required=False, min_value=LATITUDE_MIN, max_value=LATITUDE_MAX
    )
    pickup_lng = serializers.FloatField(
        required=False, min_value=LONGITUDE_MIN, max_value=LONGITUDE_MAX
    )

    def validate(self, attrs: dict) -> dict:
        if attrs.get("ordering") == RideOrdering.DISTANCE and not (
            "pickup_lat" in attrs and "pickup_lng" in attrs
        ):
            raise serializers.ValidationError(
                "pickup_lat and pickup_lng are required when ordering by distance."
            )
        return attrs
