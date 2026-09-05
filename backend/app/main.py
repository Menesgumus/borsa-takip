from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import AsyncGenerator

from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Placeholder for startup resource initialization (e.g. DB engine, Redis pool)
    yield
    # Shutdown resource cleanup
    from app.core.redis import redis_client
    from app.db.session import engine
    await redis_client.aclose()
    await engine.dispose()

from app.core.logging import CorrelationIdMiddleware
from app.core.errors import DomainException, domain_exception_handler, general_exception_handler
from app.api import health

# ... existing code ...

app = FastAPI(
    title="Borsa Takip API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
)

app.add_middleware(CorrelationIdMiddleware)
app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(health.router, prefix="/health", tags=["health"])

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Borsa Takip API is running"}

