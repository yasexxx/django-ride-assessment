# Rides API

A RESTful API built with Django REST Framework for managing ride information.

## Project Structure

This repository uses a Domain-Driven Design (DDD) approach to isolate business logic, enforce clean boundaries, and maximize modularity.

```
config/            Project config (split settings, root urls, wsgi/asgi)
apps/
  common/          Shared kernel: base models, pagination, permissions
  accounts/        User bounded context (custom email-login user)
  rides/           Ride + RideEvent bounded context
requirements/      base / dev / prod dependency sets
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

The API container waits for PostGIS, runs migrations, and serves on
http://localhost:8000.

## Running checks

```bash
docker compose run --rm web python manage.py check
```
