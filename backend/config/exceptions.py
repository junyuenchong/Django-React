from typing import Any, Optional

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def api_exception_handler(exc: Exception, context: dict[str, Any]) -> Optional[Response]:
    """
    Unified API error format:
    {
      "error": { "type": "...", "message": "..." }
    }
    """
    response = drf_exception_handler(exc, context)
    status_code = response.status_code if response is not None else 500
    message = str(exc) or "Unexpected error"

    return Response(
        {"error": {"type": exc.__class__.__name__, "message": message}},
        status=status_code,
    )

