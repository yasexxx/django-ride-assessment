"""Enable the PostGIS extension before any spatial column is created.

Runs before ``rides.0001_initial`` (which adds the geography PointField) so that
freshly-created databases have PostGIS available.
"""
from django.contrib.postgres.operations import CreateExtension
from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    dependencies: list[tuple[str, str]] = []

    run_before = [
        ("rides", "0001_initial"),
    ]

    operations = [
        CreateExtension("postgis"),
    ]
