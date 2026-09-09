from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.errors import DomainError, domain_exception_handler, general_exception_handler
from app.core.logging import CorrelationIdMiddleware
from app.core.redis import redis_client
from app.db.session import engine
from app.market.mock_provider import MockMarketDataProvider
from app.market.registry import registry
from app.market.yahoo_provider import YahooFinanceProvider


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup resource initialization
    yahoo_provider = YahooFinanceProvider()

    if settings.ENABLE_MOCK_MARKET_DATA:
        mock_provider = MockMarketDataProvider()
        registry.register(mock_provider, is_primary=True)
        registry.register(yahoo_provider, is_primary=False)
    else:
        registry.register(yahoo_provider, is_primary=True)

    yield
    # Shutdown resource cleanup
    await redis_client.aclose()
    await engine.dispose()


app = FastAPI(
    title="Borsa Takip API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(CorrelationIdMiddleware)
app.add_exception_handler(DomainError, domain_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Borsa Takip API is running"}
