"""Root URL configuration.

API routes are delegated to each bounded context under the versioned
``/api/v1/`` prefix.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.rides.urls")),
    path("api/v1/", include("apps.accounts.urls")),
]
