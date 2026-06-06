"""Shared viewset base classes."""
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.common.permissions import IsAdminRole

_STATUS_MESSAGES = {
    200: "OK",
    201: "Created Successfully",
    202: "Accepted",
}


class AdminModelViewSet(ModelViewSet):
    """Base ModelViewSet enforcing admin-only access.

    Declares the "whole API is admin-only" rule exactly once; every resource
    viewset inherits it instead of repeating ``permission_classes``.

    Also wraps every success response in the standard envelope:
    ``{"success": true, "message": "...", "data": ...}``
    so callers always see a consistent shape regardless of action.
    """

    permission_classes = [IsAdminRole]

    def finalize_response(self, request, response, *args, **kwargs) -> Response:
        response = super().finalize_response(request, response, *args, **kwargs)

        is_wrapped = isinstance(response.data, dict) and "success" in response.data

        if response.data is None or is_wrapped or response.status_code >= 400:
            return response

        response.data = {
            "success": True,
            "message": _STATUS_MESSAGES.get(response.status_code, "OK"),
            "data": response.data,
        }

        return response
