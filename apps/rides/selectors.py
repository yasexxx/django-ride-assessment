"""Read-side query construction for the rides bounded context.

Selectors own queryset shaping; views call them and stay thin.
"""
from django.db.models import Prefetch, QuerySet
from django.utils import timezone

from apps.rides.constants import RECENT_EVENTS_WINDOW, TODAYS_RIDE_EVENTS_ATTR
from apps.rides.models import Ride, RideEvent


def list_rides() -> QuerySet[Ride]:
    """Base queryset for the Ride List API.

    Returns rides with their rider/driver joined in the main query
    (``select_related``) and only the last-24h RideEvents attached via a single
    filtered
    """
    recent_cutoff = timezone.now() - RECENT_EVENTS_WINDOW
    todays_events = RideEvent.objects.filter(created_at__gte=recent_cutoff)

    return (
        Ride.objects.select_related("id_rider", "id_driver")
        .prefetch_related(
            Prefetch("events", queryset=todays_events, to_attr=TODAYS_RIDE_EVENTS_ATTR)
        )
        .order_by("id_ride")
    )
