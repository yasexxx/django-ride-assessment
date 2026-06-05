"""Project-wide DRF permissions."""
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdminRole(BasePermission):
    """Allow access only to authenticated users whose role is ``admin``.

    The admin check reads ``User.is_admin`` (which compares against
    ``User.Role.ADMIN``) — the single source of truth for the role rule.
    """

    message = "Only admin users may access this resource."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.is_admin)
