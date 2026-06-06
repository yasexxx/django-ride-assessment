"""DRF exception handler.

Registered as REST_FRAMEWORK["EXCEPTION_HANDLER"]. Wraps every error response
in the standard envelope and ensures no DB internals or stack traces leak to
the client. All unexpected errors are logged server-side at ERROR level.
"""
import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import DatabaseError, IntegrityError
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)

_MSG_VALIDATION = "Validation failed."
_MSG_INTEGRITY = "The request conflicts with existing data."
_MSG_DATABASE = "A database error occurred. Please try again later."
_MSG_UNEXPECTED = "An unexpected error occurred. Please try again later."


def _format_errors(exc: APIException) -> dict | None:
    """Convert DRF's structured detail into a plain dict of string lists."""
    detail = exc.detail
    if isinstance(detail, dict):
        return {
            field: [str(e) for e in (errs if isinstance(errs, list) else [errs])]
            for field, errs in detail.items()
        }
    if isinstance(detail, list):
        return {"non_field_errors": [str(e) for e in detail]}
    return None


def _message_for(exc: APIException) -> str:
    if isinstance(exc, ValidationError):
        return _MSG_VALIDATION
    detail = exc.detail
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list) and len(detail) == 1:
        return str(detail[0])
    return str(exc.default_detail)


def handle_exception(exc, context) -> Response | None:
    response = drf_exception_handler(exc, context)

    if response is not None:
        # DRF handled it — reformat into our envelope.
        errors = _format_errors(exc) if isinstance(exc, APIException) else None
        body: dict = {"success": False, "message": _message_for(exc)}
        if errors:
            body["errors"] = errors
        response.data = body
        return response

    # Beyond DRF's knowledge — handle DB and unknown exceptions safely.
    if isinstance(exc, IntegrityError):
        logger.warning("IntegrityError caught: %s", exc, exc_info=True)
        return Response(
            {"success": False, "message": _MSG_INTEGRITY},
            status=status.HTTP_409_CONFLICT,
        )

    if isinstance(exc, DatabaseError):
        logger.error("DatabaseError caught: %s", exc, exc_info=True)
        return Response(
            {"success": False, "message": _MSG_DATABASE},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, DjangoValidationError):
        messages = list(exc.messages) if hasattr(exc, "messages") else [str(exc)]
        return Response(
            {
                "success": False,
                "message": _MSG_VALIDATION,
                "errors": {"non_field_errors": messages},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    logger.critical("Unhandled exception in view: %s", exc, exc_info=True)
    return Response(
        {"success": False, "message": _MSG_UNEXPECTED},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
