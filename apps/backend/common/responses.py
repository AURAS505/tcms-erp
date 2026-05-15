from rest_framework import status
from rest_framework.response import Response


def response_envelope(*, success: bool, data=None, message: str = "", errors=None, meta=None) -> dict:
    return {
        "success": success,
        "data": data if data is not None else {},
        "message": message,
        "errors": errors,
        "meta": meta if meta is not None else {},
    }


def api_success(data=None, *, message: str = "", meta=None, status_code: int = status.HTTP_200_OK) -> Response:
    return Response(
        response_envelope(success=True, data=data, message=message, errors=None, meta=meta),
        status=status_code,
    )


def api_error(
    *,
    message: str,
    errors=None,
    data=None,
    meta=None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> Response:
    return Response(
        response_envelope(success=False, data=data, message=message, errors=errors or {}, meta=meta),
        status=status_code,
    )


def validation_error_response(errors, *, message: str = "Validation failed") -> Response:
    return api_error(message=message, errors=errors, status_code=status.HTTP_400_BAD_REQUEST)
