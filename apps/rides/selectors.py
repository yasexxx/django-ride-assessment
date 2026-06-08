"""Read-side query construction for the rides bounded context.

Selectors own queryset shaping; views call them and stay thin.
"""
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django.db.models import F, FloatField, Func, Prefetch, QuerySet, Value
from django.utils import timezone

from apps.common.constants import WGS84_SRID
from apps.rides.constants import (
    RECENT_EVENTS_WINDOW,
    TODAYS_RIDE_EVENTS_ATTR,
    TODAYS_RIDE_EVENTS_LIMIT,
    RideOrdering,
)
from apps.rides.models import Ride, RideEvent


class KnnDistance(Func):
    """PostGIS KNN distance operator: ``geom_a <-> geom_b``.

    Ordering by this lets PostgreSQL use the GiST index on ``pickup_point`` for
    an index-ordered nearest-neighbour scan — O(log n) + limit — instead of the
    full-table ``ST_Distance`` computation a plain ``Distance()`` ordering would
    force. It is an ORM expression (not
    raw SQL); the ``<->`` operator simply has no built-in GeoDjango wrapper.
    """

    arg_joiner = " <-> "
    template = "%(expressions)s"
    output_field = FloatField()


def list_rides() -> QuerySet[Ride]:
    """Base queryset for the Ride List API.

    Returns rides with their rider/driver joined in the main query
    (``select_related``) and only the last-24h RideEvents attached via a single
    filtered
    """
    recent_cutoff = timezone.now() - RECENT_EVENTS_WINDOW
    todays_events = RideEvent.objects.filter(created_at__gte=recent_cutoff).order_by(
        "-created_at", "-id_ride_event"
    )[:TODAYS_RIDE_EVENTS_LIMIT]

    return (
        Ride.objects.select_related("id_rider", "id_driver")
        .prefetch_related(
            Prefetch("events", queryset=todays_events, to_attr=TODAYS_RIDE_EVENTS_ATTR)
        )
        .order_by("id_ride")
    )


def order_rides(
    rides: QuerySet[Ride],
    *,
    ordering: str | None = None,
    pickup_point: Point | None = None,
) -> QuerySet[Ride]:
    """Apply the requested sort to a Ride queryset.

    - ``distance``: nearest-first via the GiST-indexed KNN operator.
    - ``pickup_time`` / ``-pickup_time``: with an ``id_ride`` tiebreaker so
      pagination is deterministic across pages.
    - otherwise: the base ordering from ``list_rides`` (``id_ride``) is kept.
    """
    if ordering == RideOrdering.DISTANCE and pickup_point is not None:
        reference = Value(
            pickup_point,
            output_field=PointField(geography=True, srid=WGS84_SRID),
        )
        # No secondary key: a second ORDER BY column would defeat the KNN scan.
        return rides.order_by(KnnDistance(F("pickup_point"), reference))

    if ordering in RideOrdering.PICKUP_TIME:
        return rides.order_by(ordering, "id_ride")

    return rides


def build_ride_list_queryset(validated_data: dict) -> QuerySet[Ride]:
    """Assemble the queryset for the Ride List API from pre-validated query params.

    Centralises coordinate construction and ordering so the view stays thin.
    Must be called with data from ``RideListQuerySerializer.validated_data``.
    """
    ordering = validated_data.get("ordering")
    pickup_point = None
    if ordering == RideOrdering.DISTANCE:
        pickup_point = Point(
            validated_data["pickup_lng"],
            validated_data["pickup_lat"],
            srid=WGS84_SRID,
        )
    return order_rides(list_rides(), ordering=ordering, pickup_point=pickup_point)
