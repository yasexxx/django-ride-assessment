FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System libraries: GeoDjango (GDAL/GEOS/PROJ) + Postgres client headers.
RUN apt-get update && apt-get install -y --no-install-recommends \
        binutils \
        gdal-bin \
        libgdal-dev \
        libgeos-dev \
        libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Run as a non-root user. UID/GID 1000 matches the typical host developer so
# files written into the mounted volume (e.g. new migrations) stay host-owned.
RUN groupadd --gid 1000 app && useradd --uid 1000 --gid 1000 --create-home app

WORKDIR /app

# Install Python deps first for better layer caching.
# Override with --build-arg REQUIREMENTS=requirements/prod.txt for production images.
ARG REQUIREMENTS=requirements/dev.txt
COPY requirements/ requirements/
RUN pip install --upgrade pip && pip install -r ${REQUIREMENTS}

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER app

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
