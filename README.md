# Rides API

A RESTful API built with Django REST Framework for managing ride information.

## Table of Contents

- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Quickstart (Docker)](#quickstart-docker)
- [Quickstart (local, without Docker)](#quickstart-local-without-docker)
- [Running checks](#running-checks)
- [Router pattern](#router-pattern)
- [Constants convention](#constants-convention)
- [Authentication](#authentication)
- [Filtering and ordering rides](#filtering-and-ordering-rides)
- [Seeding development data](#seeding-development-data)
- [Response envelope](#response-envelope)
- [Error handling](#error-handling)
- [Example: Ride List response](#example-ride-list-response)
- [Performance of the Ride List API](#performance-of-the-ride-list-api)
- [SQL Report (Bonus): trips over 1 hour, by month and driver](#sql-report-bonus-trips-over-1-hour-by-month-and-driver)
- [Design decisions & challenges](#design-decisions--challenges)

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
    views.py         UserViewSet
    urls.py          Registers UserViewSet on the shared router
  rides/             Ride + RideEvent bounded context
    constants.py     Bounded-context constants (RECENT_EVENTS_WINDOW, TODAYS_RIDE_EVENTS_ATTR, RideOrdering)
    filters.py       django-filter FilterSet for rides (status, rider_email)
    models.py        Ride, RideEvent
    selectors.py     Read-side queryset builders (list_rides, KNN nearest-neighbour ordering)
    serializers.py   RideSerializer, RideListSerializer, RideEventSerializer
    views.py         RideViewSet, RideEventViewSet
    urls.py          Registers viewsets on the shared router

  accounts/
    management/
      commands/
        seed.py      Management command to seed initial rider and driver users

requirements/
  base.txt           Core dependencies
  dev.txt            Development extras
  prod.txt           Production extras
```

## Requirements

**Docker (recommended)**
- [Docker](https://docs.docker.com/get-docker/) 24+ with the Compose plugin (included in Docker Desktop)

**Local development (without Docker)**
- [Python 3.12+](https://www.python.org/downloads/)
- [PostgreSQL 16](https://www.postgresql.org/download/) with the [PostGIS](https://postgis.net/install/) extension
- GDAL, GEOS, and PROJ system libraries — see the [GeoDjango installation guide](https://docs.djangoproject.com/en/stable/ref/contrib/gis/install/geolibs/)
- [pip](https://pip.pypa.io/en/stable/installation/) (bundled with Python 3.12+)

## Quickstart (Docker)

```bash
cp .env.example .env
docker compose up --build -d
```

The API container waits for PostGIS, runs migrations, and serves on http://localhost:8000.

## Quickstart (local, without Docker for Windows & Ubuntu)

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements/dev.txt

# 3. Configure environment
cp .env.example .env
# Edit .env: change POSTGRES_HOST=db → POSTGRES_HOST=localhost
# Update POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB to match your local setup
```

Create the database (run as a PostgreSQL superuser). The user needs `SUPERUSER` so the first migration can run `CREATE EXTENSION postgis` — matching what Docker's postgres image does automatically:

```sql
CREATE USER rides WITH SUPERUSER PASSWORD 'rides';
CREATE DATABASE rides OWNER rides;
```

```bash
# 4. Apply migrations
python manage.py migrate

# 5. Create an admin user (required — all endpoints are admin-only)
python manage.py createsuperuser

# 6. (Optional) Seed riders and drivers
python manage.py seed

# 7. Start the development server
python manage.py runserver
```

The API is now available at http://localhost:8000.

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
router.register("ride-events", RideEventViewSet, basename="ride-event")

# config/urls.py
from config.router import router
urlpatterns = [
    path("api/v1/", include((router.urls, "api"), namespace="api")),
    ...
]
```

The router is mounted under the `api` namespace, so reverse lookups are
`api:ride-list`, `api:ride-detail`, `api:user-list`, etc. This keeps route
registration co-located with each bounded context while avoiding the
duplication of a versioned prefix in every app.

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

## Filtering and ordering rides

`GET /api/v1/rides/` accepts the following query parameters:

| Parameter | Type | Description |
|---|---|---|
| `status` | string | Filter by ride status (one of the `Ride.Status` choices: `en-route`, `pickup`, `dropoff`) |
| `rider_email` | string | Filter by exact rider email address |
| `ordering` | string | `pickup_time` / `-pickup_time`, or `distance` (nearest-first) |
| `pickup_lat`, `pickup_lng` | float | Reference GPS point — **required** when `ordering=distance` |
| `page`, `page_size` | int | Pagination (default page size 20, max 100) |

Examples:

```bash
# Filter + sort by pickup time, paginated
GET /api/v1/rides/?status=pickup&ordering=-pickup_time&page_size=50

# Filter rider's email
GET /api/v1/rides/?rider_email=example@email.com

# Sort by distance to a GPS point (nearest first)
GET /api/v1/rides/?ordering=distance&pickup_lat=14.5547&pickup_lng=121.0244
```

Proximity ordering uses the PostGIS KNN operator (`<->`) to perform an index-ordered nearest-neighbour scan via the GiST index on `pickup_point`, avoiding a full-table distance computation. The sort parameters are validated (e.g. `distance` without coordinates, or an out-of-range latitude, returns `400`).

## Seeding development data

A management command seeds the database with a default set of riders and drivers:

```bash
docker compose run --rm web python manage.py seed
```

This creates 10 riders (`rider_1@email.com` … `rider_10@email.com`) and 10 drivers (`driver_1@email.com` … `driver_10@email.com`), all with password `Test12345`. Existing users are skipped (idempotent).

> **Create an admin to use the API.** The endpoints are admin-only and `seed`
> does not create an admin user. Create one with:
>
> ```bash
> docker compose run --rm web python manage.py createsuperuser
> ```
>
> `createsuperuser` sets `role=admin` (see `UserManager.create_superuser`), so
> the resulting account satisfies the `IsAdminRole` permission. The `seed`
> command intentionally creates only riders/drivers; it does not generate rides
> or ride events, so the SQL report below assumes a populated dataset (as the
> assessment permits).

## Response envelope

Every response is wrapped in a consistent envelope:

**Success**
```json
{"success": true, "message": "OK.", "data": { ... }}
```

**Error**
```json
{"success": false, "message": "Validation failed.", "errors": {"field": ["msg"]}}
```

For paginated list endpoints, `data` contains the DRF pagination shape (`count`, `next`, `previous`, `results`).

## Error handling

All exceptions are caught by a central handler (`apps/common/exception_handler.py`) registered as DRF's `EXCEPTION_HANDLER`. It guarantees:

| Exception | HTTP | Client message |
|---|---|---|
| DRF `ValidationError` | 400 | Field-level `errors` dict |
| DRF `NotAuthenticated` | 401 | Safe detail string |
| DRF `PermissionDenied` | 403 | Safe detail string |
| `IntegrityError` | 409 | "The request conflicts with existing data." |
| `DatabaseError` | 500 | "A database error occurred." |
| Unhandled | 500 | "An unexpected error occurred." |

DB errors are logged server-side at `ERROR`/`CRITICAL` level with full tracebacks; the client only receives a generic safe message — no SQL, schema names, or internal details are ever exposed.

## Example: Ride List response

`GET /api/v1/rides/` returns a paginated list. Each ride embeds the related
rider and driver and a `todays_ride_events` array (RideEvents from the last 24
hours only):

```json
{
  "success": true,
  "message": "OK.",
  "data": {
    "count": 42,
    "next": "http://localhost:8000/api/v1/rides/?page=2",
    "previous": null,
    "results": [
      {
        "id_ride": 1,
        "status": "en-route",
        "id_rider": {"id_user": 5, "role": "rider", "first_name": "Ada",
                     "last_name": "Lovelace", "email": "ada@example.com",
                     "phone_number": "+1..."},
        "id_driver": {"id_user": 9, "role": "driver", "first_name": "Chris",
                      "last_name": "Halls", "email": "chris@example.com",
                      "phone_number": "+1..."},
        "pickup_latitude": 14.5547, "pickup_longitude": 121.0244,
        "dropoff_latitude": 14.5995, "dropoff_longitude": 120.9842,
        "pickup_time": "2024-01-10T08:00:00Z",
        "todays_ride_events": [
          {"id_ride_event": 12, "id_ride": 1,
           "description": "Status changed to pickup",
           "created_at": "2024-01-10T08:02:00Z"}
        ]
      }
    ]
  }
}
```

## Performance of the Ride List API

The list endpoint returns the rides, their related rider/driver, and recent
events in **3 queries total**, independent of the number of rides:

1. `COUNT(*)` for pagination,
2. the rides joined to rider + driver via `select_related`,
3. a single filtered `Prefetch` for the last-24h `RideEvent`s.

`todays_ride_events` is built from that filtered `Prefetch` (`created_at >= now -
24h`), so the full `RideEvent` table is **never** loaded — important because that
table is expected to grow very large. Query construction lives in
`apps/rides/selectors.py`; the view stays thin.

## SQL Report (Bonus): trips over 1 hour, by month and driver

Counts trips whose duration from pickup to dropoff exceeded one hour, grouped by
month and driver. Trip duration is the gap between each ride's
`'Status changed to pickup'` and `'Status changed to dropoff'` RideEvents.

```sql
SELECT
    SUBSTR(CAST(pickup.created_at AS VARCHAR), 1, 7) AS month,
    driver.first_name || ' ' || SUBSTR(driver.last_name, 1, 1) AS driver,
    COUNT(*) AS count_of_trips_over_1_hour
FROM ride AS r
JOIN ride_event AS pickup
      ON pickup.id_ride = r.id_ride
JOIN ride_event AS dropoff
      ON dropoff.id_ride = r.id_ride
JOIN "user" AS driver
      ON driver.id_user = r.id_driver
WHERE dropoff.created_at > pickup.created_at + INTERVAL '1 hour'
  AND pickup.description = 'Status changed to pickup'
  AND dropoff.description = 'Status changed to dropoff'
GROUP BY SUBSTR(CAST(pickup.created_at AS VARCHAR), 1, 7),
         driver.id_user, driver.first_name, driver.last_name
ORDER BY month, driver;
```

Sample output:

| month | driver | count_of_trips_over_1_hour |
|---|---|---|
| 2024-01 | Chris H | 4 |
| 2024-01 | Howard Y | 5 |
| 2024-02 | Chris H | 7 |

Notes:
- `"user"` is quoted because `user` is a reserved word in PostgreSQL. The ORM
  quotes all identifiers automatically; only hand-written SQL needs this.
- Grouping is by the driver's identity (`id_user`); the `first_name + last
  initial` form is just the display label (matching the assessment sample).
- Assumes one pickup and one dropoff event per ride, as described in the brief.
  Populating `ride_event` is out of scope per the assessment.

## Design decisions & challenges

- **Domain-oriented modular monolith.** Bounded contexts as Django apps
  (`accounts`, `rides`) with a `common` shared kernel. Read queries live in
  `selectors.py`, HTTP orchestration in thin viewsets, and the ORM model is the
  single source of truth for data — DDD value without fighting Django by adding
  a parallel domain/repository layer.
- **Custom email-login User** (`AbstractBaseUser` + `PermissionsMixin`) mapped to
  the spec's `user` table, with a `role` field driving the `IsAdminRole`
  permission. The admin-only rule is declared once on an `AdminModelViewSet`
  base and inherited by every resource viewset.
- **Response envelope via `finalize_response` override.** Success wrapping
  (`{"success": true, "message": "...", "data": ...}`) is applied in
  `AdminModelViewSet.finalize_response` rather than middleware or a custom
  renderer. This scopes the envelope to API ViewSets only — Django admin and
  other non-DRF views are unaffected. Error responses are wrapped by the central
  `exception_handler` using the same shape.
- **PostGIS for efficient distance sort.** `pickup_point` is a geography
  `PointField` kept in sync from the lat/long columns in `Ride.save()`, with a
  GiST index. Distance sorting uses the KNN `<->` operator
  (`apps/rides/selectors.py: KnnDistance`) for an index-ordered nearest-neighbour
  scan, rather than a per-row `ST_Distance` computation.
  - *Challenge / trade-off:* with `select_related` joining rider/driver, the
    planner may add a final sort of the joined rows because hash joins don't
    preserve order. The GiST index still provides the ordered nearest-neighbour
    scan, and on a large table with a `LIMIT` the planner can pick an
    index-ordered nested-loop join — keeping the total query count at 3
    regardless of result set size.
- **Pagination choice.** `PageNumberPagination` (offset-style) is used because
  distance ordering is computed per-request; cursor pagination can't paginate a
  dynamic KNN ordering. Pagination is verified to work under both sort modes.
- **Filtering** goes through a django-filter `FilterSet` (`status`,
  `rider_email` via the rider FK), never manual query-param parsing.
- **Sort-parameter validation via a dedicated serializer.** `RideListQuerySerializer`
  validates `ordering`, `pickup_lat`, and `pickup_lng` in the view before the
  queryset is built, returning a structured 400 when `distance` ordering is
  requested without coordinates or when coordinates are out of range. This keeps
  validation logic out of the selector and decoupled from the filter backend.
- **Role enforcement in write serializers.** `RideSerializer.validate_id_rider`
  and `validate_id_driver` reject FK values whose `role` doesn't match the
  expected role (`rider` / `driver`), returning field-level errors through the
  standard envelope rather than allowing a model-level silent mismatch.
- **Explicit database indexes.** Beyond the GiST index on `pickup_point`, the
  schema declares `ride_status_idx` and `ride_pickup_time_idx` on `Ride`, and a
  composite `(id_ride, created_at)` index on `RideEvent`. The composite index
  directly supports the filtered `Prefetch` in the list API (events per ride
  within a time window) and the join pattern in the SQL duration report.
- **PostGIS in tests/fresh DBs.** A `CreateExtension('postgis')` migration in
  `apps/common` runs (via `run_before`) ahead of the spatial column so any
  freshly-created database has PostGIS enabled.
