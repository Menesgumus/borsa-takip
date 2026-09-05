from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import AsyncGenerator

from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Placeholder for startup resource initialization (e.g. DB engine, Redis pool)
    yield
    # Placeholder for shutdown resource cleanup

app = FastAPI(
    title="Borsa Takip API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
)

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Borsa Takip API is running"}
