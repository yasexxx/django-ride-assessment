"""Accounts API routes."""
from config.router import router

from apps.accounts.views import UserViewSet

router.register("users", UserViewSet, basename="user")
