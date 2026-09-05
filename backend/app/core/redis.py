from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.core.config import settings

# Bounded connection pool for Redis
redis_client = Redis.from_url(
    settings.REDIS_URL, decode_responses=True, socket_timeout=5.0, socket_connect_timeout=5.0
)


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    try:
        yield redis_client
    finally:
        pass  # The client pool is global, we don't close it per request
