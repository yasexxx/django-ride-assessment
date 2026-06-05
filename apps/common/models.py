"""Shared kernel: abstract base models reused across bounded contexts."""
from django.db import models


class TimeStampedModel(models.Model):
    """Adds self-managed ``created_at`` / ``updated_at`` timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
