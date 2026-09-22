import os
from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.core.config import settings


import fakeredis

if os.environ.get("USE_MOCK_REDIS", "").lower() == "true" or (settings.ENVIRONMENT == "test" and not settings.REDIS_URL):
    redis_client = fakeredis.FakeAsyncRedis(decode_responses=True)
else:
    redis_client = Redis.from_url(
        settings.REDIS_URL, decode_responses=True, socket_timeout=5.0, socket_connect_timeout=5.0
    )

async def get_redis_client() -> AsyncGenerator[Redis, None]:
    try:
        yield redis_client  # type: ignore
    finally:
        pass
