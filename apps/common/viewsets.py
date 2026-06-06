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

        # 204 No Content has no body — leave it alone.
        if response.data is None:
            return response

        # Already wrapped by the exception handler (error path).
        if isinstance(response.data, dict) and "success" in response.data:
            return response

        if response.status_code < 400:
            response.data = {
                "success": True,
                "message": _STATUS_MESSAGES.get(response.status_code, "OK"),
                "data": response.data,
            }

        return response
