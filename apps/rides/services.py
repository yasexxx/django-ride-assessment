"""Write-side business logic for the rides bounded context."""
from apps.rides.models import Ride, RideEvent


def create_ride(data: dict) -> Ride:
    return Ride.objects.create(**data)


def update_ride(instance: Ride, data: dict) -> Ride:
    for attr, value in data.items():
        setattr(instance, attr, value)
    instance.save()
    return instance


def create_ride_event(data: dict) -> RideEvent:
    return RideEvent.objects.create(**data)
