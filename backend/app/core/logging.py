import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id or len(correlation_id) > 64:
            correlation_id = str(uuid.uuid4())

        request.state.correlation_id = correlation_id

        start_time = time.time()
        try:
            response = await call_next(request)
        except Exception as e:
            # Re-raise to let exception handlers catch it
            raise e
        finally:
            _elapsed = time.time() - start_time  # noqa: F841 — will wire to structured logging
            # Log: path, method, status, elapsed, correlation_id

        response.headers["X-Correlation-ID"] = correlation_id
        return response
