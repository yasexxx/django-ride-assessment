"""Serializers for the rides bounded context.

Phase 3 provides the write/detail serializers used by CRUD. The read-optimised
list serializer (nested events, rider/driver, ``todays_ride_events``) is added
in a later phase via ``get_serializer_class`` — extension, not modification.
"""
from rest_framework import serializers

from apps.rides.models import Ride, RideEvent


class RideEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideEvent
        fields = ["id_ride_event", "id_ride", "description", "created_at"]
        read_only_fields = ["id_ride_event", "created_at"]


class RideSerializer(serializers.ModelSerializer):
    """Write/detail serializer. ``pickup_point`` is derived, so it is omitted."""

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
