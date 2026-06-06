# Rides API

A RESTful API built with Django REST Framework for managing ride information.

## Project Structure

This repository uses a Domain-Driven Design (DDD) approach to isolate business logic, enforce clean boundaries, and maximize modularity.

```
config/
  router.py          Single shared DefaultRouter instance — all apps register here
  urls.py            Root URL conf; mounts api/v1/ from router.urls
  settings/
    base.py          Single source of truth for all settings
    dev.py           Development overrides
    prod.py          Production overrides
    env.py           Typed env-var helpers (env_str, env_bool, env_list)
  wsgi.py / asgi.py

apps/
  common/            Shared kernel
    constants.py     Project-wide constants (e.g. WGS84_SRID)
    models.py        TimeStampedModel base
    pagination.py    DefaultPagination
    permissions.py   IsAdminRole permission class
    viewsets.py      AdminModelViewSet base
  accounts/          User bounded context
    constants.py     (add here if accounts-specific constants are needed)
    managers.py      UserManager (email-based creation helpers)
    models.py        Custom User model (email login, role field)
    serializers.py   UserSerializer
    views.py         UserViewSet, ObtainAuthToken
    urls.py          Registers UserViewSet on the shared router; auth/token/ endpoint
  rides/             Ride + RideEvent bounded context
    constants.py     Bounded-context constants (RECENT_EVENTS_WINDOW, TODAYS_RIDE_EVENTS_ATTR)
    models.py        Ride, RideEvent
    selectors.py     Read-side queryset builders (list_rides)
    serializers.py   RideSerializer, RideListSerializer, RideEventSerializer
    views.py         RideViewSet, RideEventViewSet
    urls.py          Registers viewsets on the shared router

requirements/
  base.txt           Core dependencies
  dev.txt            Development extras
  prod.txt           Production extras
```

## Requirements

**Docker (recommended)**
- [Docker](https://docs.docker.com/get-docker/) 24+ with the Compose plugin (included in Docker Desktop)

**Local development (without Docker)**
- Python 3.12+
- PostgreSQL 16 with the [PostGIS](https://postgis.net/install/) extension
- GDAL, GEOS, and PROJ system libraries (required by GeoDjango)

## Quickstart (Docker)

```bash
cp .env.example .env
docker compose up --build -d
```

The API container waits for PostGIS, runs migrations, and serves on http://localhost:8000.

## Running checks

```bash
docker compose run --rm web python manage.py check
```

## Router pattern

All API routes are registered on a single `DefaultRouter` instance defined in `config/router.py`. Each app's `urls.py` imports that router and calls `router.register(...)` — no app-level `urlpatterns` needed for ViewSets.

```python
# config/router.py
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

# apps/rides/urls.py
from config.router import router
from apps.rides.views import RideViewSet, RideEventViewSet

router.register("rides", RideViewSet, basename="ride")
router.register("ride-events", RideEventViewSet, basename="rideevent")

# config/urls.py
from config.router import router
urlpatterns = [
    path("api/v1/", include(router.urls)),
    ...
]
```

This keeps route registration co-located with each bounded context while avoiding the duplication of a versioned prefix in every app.

## Constants convention

Constants live at two scopes:

| File | Scope | Examples |
|---|---|---|
| `apps/common/constants.py` | Project-wide | `WGS84_SRID` |
| `apps/<app>/constants.py` | Bounded-context | `RECENT_EVENTS_WINDOW`, `TODAYS_RIDE_EVENTS_ATTR` |

Prefer app-scoped constants unless a value is genuinely shared across multiple bounded contexts. Never inline magic values in model fields, serializers, or views — reference the constant by name so the intent is searchable and the value is changed in one place.

## Authentication

The API supports two authentication methods, tried in order on each request:

| Method | How to use |
|---|---|
| Session | Log in via `/admin/`, then include the session cookie |
| Basic | `Authorization: Basic <base64(email:password)>` |

All routes require the authenticated user to have `role = "admin"` (`IsAdminRole` permission).

Use it on subsequent requests with DRF Interface:

```bash
curl http://localhost:8000/api/v1/rides/
```

Note: To access Django Rest Framework (DRF) inteface must be logged in as admin user. [Learn more.](https://www.w3schools.com/django/django_admin_create_user.php)

