"""Constants for the rides bounded context."""
from datetime import timedelta

# The Ride List API surfaces only RideEvents from the last 24 hours.
RECENT_EVENTS_WINDOW = timedelta(hours=24)

# Attribute the filtered Prefetch writes onto each Ride instance. Must match the
# ``RideListSerializer.todays_ride_events`` field name.
TODAYS_RIDE_EVENTS_ATTR = "todays_ride_events"
