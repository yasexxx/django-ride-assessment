"""Root URL configuration.

API routes are delegated to each bounded context under the versioned
``/api/v1/`` prefix.
"""
from django.contrib import admin
from django.urls import include, path

# Fixed: Import only for side effects - main route registration
import apps.accounts.urls
import apps.rides.urls

from config.router import router

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include((router.urls, "api"), namespace="api")),
]
