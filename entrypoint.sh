#!/usr/bin/env bash
set -e

# The db service is gated by a healthcheck in docker-compose, so by the time we
# run, Postgres is accepting connections. Apply migrations, then hand off.
python manage.py migrate --noinput

exec "$@"
