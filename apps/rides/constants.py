"""Constants for the rides bounded context."""
from datetime import timedelta

# The Ride List API surfaces only RideEvents from the last 24 hours.
RECENT_EVENTS_WINDOW = timedelta(hours=24)

# Maximum number of recent RideEvents exposed per Ride in the list API.
TODAYS_RIDE_EVENTS_LIMIT = 100

# Attribute the filtered Prefetch writes onto each Ride instance. Must match the
# ``RideListSerializer.todays_ride_events`` field name.
TODAYS_RIDE_EVENTS_ATTR = "todays_ride_events"


class RideOrdering:
    """Allowed values for the Ride List ``ordering`` query parameter.

    ``pickup_time`` / ``-pickup_time`` map straight to model-field ordering;
    ``distance`` orders by proximity to a supplied GPS point (requires
    ``pickup_lat`` / ``pickup_lng``).
    """

    PICKUP_TIME_ASC = "pickup_time"
    PICKUP_TIME_DESC = "-pickup_time"
    DISTANCE = "distance"

    PICKUP_TIME = (PICKUP_TIME_ASC, PICKUP_TIME_DESC)
    ALL = (PICKUP_TIME_ASC, PICKUP_TIME_DESC, DISTANCE)
