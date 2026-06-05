"""Shared viewset base classes."""
from rest_framework.viewsets import ModelViewSet

from apps.common.permissions import IsAdminRole


class AdminModelViewSet(ModelViewSet):
    """Base ModelViewSet enforcing admin-only access.

    Declares the "whole API is admin-only" rule exactly once; every resource
    viewset inherits it instead of repeating ``permission_classes``.
    """

    permission_classes = [IsAdminRole]
