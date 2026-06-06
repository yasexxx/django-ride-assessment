"""Filtering for the rides bounded context (django-filter FilterSet)."""
from django_filters import rest_framework as filters

from apps.rides.models import Ride


class RideFilter(filters.FilterSet):
    """Filters for the Ride List API: by status and by rider email.

    ``rider_email`` traverses the rider FK (``id_rider__email``). Exact match is
    used deliberately: email is unique-indexed.
    """

    status = filters.ChoiceFilter(choices=Ride.Status.choices)
    rider_email = filters.CharFilter(field_name="id_rider__email", lookup_expr="exact")

    class Meta:
        model = Ride
        fields = ["status", "rider_email"]
