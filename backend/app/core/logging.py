import uuid
import time
from typing import Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
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
            process_time = time.time() - start_time
            # Here we would log the request context: path, method, status, process_time, correlation_id.
            # Real logging setup is deferred/abstracted for now.
        
        response.headers["X-Correlation-ID"] = correlation_id
        return response
