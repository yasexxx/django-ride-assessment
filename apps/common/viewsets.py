"""Shared viewset base classes."""
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.common.permissions import IsAdminRole

_STATUS_MESSAGES = {
    200: "OK",
    201: "Created Successfully",
}


class ResponseEnvelopeMixin:
    """Wraps success responses in the standard API envelope.

    Shape: ``{"success": true, "message": "...", "data": ...}``

    Kept separate from auth so any future viewset can use the envelope
    without being tied to the admin permission rule.
    """

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


class AdminOnlyMixin:
    """Enforces admin-only access. Declared once, inherited everywhere."""

    permission_classes = [IsAdminRole]


class AdminModelViewSet(AdminOnlyMixin, ResponseEnvelopeMixin, ModelViewSet):
    """Composed base: admin gate + standard response envelope."""
