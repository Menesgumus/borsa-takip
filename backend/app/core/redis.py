import os
from collections.abc import AsyncGenerator
from redis.asyncio import Redis
from app.core.config import settings

class MockRedis:
    async def get(self, *args, **kwargs): return None
    async def set(self, *args, **kwargs): return True
    async def delete(self, *args, **kwargs): return 0
    async def incr(self, *args, **kwargs): return 1
    async def expire(self, *args, **kwargs): return True

if os.environ.get("ENVIRONMENT") == "test" or os.environ.get("CI") == "true":
    redis_client = MockRedis()
else:
    redis_client = Redis.from_url(
        settings.REDIS_URL, decode_responses=True, socket_timeout=5.0, socket_connect_timeout=5.0
    )

async def get_redis_client() -> AsyncGenerator[Redis, None]:
    try:
        yield redis_client
    finally:
        pass
