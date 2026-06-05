"""Ride bounded context: Ride and RideEvent domain models."""
from django.conf import settings
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django.db import models

from apps.common.constants import WGS84_SRID
from apps.common.models import TimeStampedModel


class Ride(TimeStampedModel):
    class Status(models.TextChoices):
        EN_ROUTE = "en-route", "En route"
        PICKUP = "pickup", "Pickup"
        DROPOFF = "dropoff", "Dropoff"

    id_ride = models.BigAutoField(primary_key=True)
    status = models.CharField(max_length=20, choices=Status.choices)

    # FKs named to match the assessment schema; the Ride List API exposes the
    # related rider/driver as ``id_rider`` / ``id_driver``. Referenced via
    # AUTH_USER_MODEL rather than importing the concrete User model.
    id_rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="rides_as_rider",
        db_column="id_rider",
    )
    id_driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="rides_as_driver",
        db_column="id_driver",
    )

    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    pickup_time = models.DateTimeField()

    # Spatially-indexed (GiST) copy of the pickup coordinates, kept in sync in
    # save(). Lets distance queries use the index instead of scanning every row.
    # editable=False / null=True: it is derived data, never set by clients.
    pickup_point = PointField(
        geography=True,
        srid=WGS84_SRID,
        null=True,
        editable=False,
    )

    class Meta:
        db_table = "ride"
        indexes = [
            models.Index(fields=["status"], name="ride_status_idx"),
            models.Index(fields=["pickup_time"], name="ride_pickup_time_idx"),
        ]

    def __str__(self) -> str:
        return f"Ride {self.pk} ({self.status})"

    def save(self, *args, **kwargs) -> None:
        # Keep the indexed point in sync with the canonical lat/long columns.
        self.pickup_point = Point(
            self.pickup_longitude, self.pickup_latitude, srid=WGS84_SRID
        )
        super().save(*args, **kwargs)


class RideEvent(TimeStampedModel):
    id_ride_event = models.BigAutoField(primary_key=True)
    id_ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name="events",
        db_column="id_ride",
    )
    description = models.CharField(max_length=255)

    class Meta:
        db_table = "ride_event"
        # Composite index supports the "events in the last 24h, per ride" lookup
        # used by the Ride List API and the monthly trip-duration report.
        indexes = [
            models.Index(fields=["id_ride", "created_at"], name="ride_event_ride_created_at_idx"),
        ]

    def __str__(self) -> str:
        return f"RideEvent {self.pk}: {self.description}"
