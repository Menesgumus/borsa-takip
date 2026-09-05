from typing import Any, Optional
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict[str, Any]] = None
    correlation_id: Optional[str] = None

class ErrorEnvelope(BaseModel):
    error: ErrorDetail

class DomainException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: Optional[dict[str, Any]] = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details

async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", None)
    error = ErrorDetail(
        code=exc.code,
        message=exc.message,
        details=exc.details,
        correlation_id=correlation_id
    )
    return JSONResponse(status_code=exc.status_code, content={"error": error.model_dump(exclude_none=True)})

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", None)
    error = ErrorDetail(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred.",
        correlation_id=correlation_id
    )
    return JSONResponse(status_code=500, content={"error": error.model_dump(exclude_none=True)})
