import logging

from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from sqlalchemy import text

from app.core.redis import redis_client
from app.db.session import engine

router = APIRouter()


class HealthStatus(BaseModel):
    status: str


@router.get("/live", response_model=HealthStatus)
async def liveness() -> HealthStatus:
    return HealthStatus(status="ok")


@router.get("/ready", response_model=HealthStatus)
async def readiness(response: Response) -> HealthStatus:
    is_ready = True

    # DB Check
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        logging.error("Database readiness check failed")
        is_ready = False

    # Redis Check
    try:
        if not await redis_client.ping():
            is_ready = False
    except Exception:
        logging.error("Redis readiness check failed")
        is_ready = False

    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthStatus(status="error")

    return HealthStatus(status="ok")
