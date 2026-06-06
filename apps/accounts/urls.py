"""Accounts API routes."""
from config.router import router

from apps.accounts.views import UserViewSet

app_name = "accounts"

router.register("users", UserViewSet, basename="user")

urlpatterns = router.urls
