from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response
from rest_framework.views import exception_handler


def _message_from_details(details: object) -> str:
    if isinstance(details, dict):
        for value in details.values():
            return _message_from_details(value)
    if isinstance(details, list) and details:
        return _message_from_details(details[0])
    if isinstance(details, ErrorDetail | str):
        return str(details)
    return "The request could not be processed."


def api_exception_handler(exc, context):
    """Return predictable, safe error envelopes for all DRF exceptions."""

    response = exception_handler(exc, context)
    if response is None:
        if isinstance(exc, ProtectedError):
            response = Response(
                {"detail": "This record is referenced by other records and cannot be deleted."},
                status=status.HTTP_409_CONFLICT,
            )
        elif isinstance(exc, IntegrityError):
            response = Response(
                {"detail": "The request conflicts with an existing record."},
                status=status.HTTP_409_CONFLICT,
            )
        elif isinstance(exc, DjangoValidationError):
            response = Response(
                getattr(exc, "message_dict", {"detail": exc.messages}),
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return None

    details = response.data
    default_code = getattr(exc, "default_code", "error")
    response.data = {
        "error": {
            "code": default_code,
            "message": _message_from_details(details),
            "details": details,
        }
    }
    return response
