import os
from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.core.config import settings


class MockRedis:
    def __init__(self):
        self.store = {}
    async def get(self, name, *args, **kwargs): return self.store.get(name)
    async def set(self, name, value, *args, **kwargs):
        self.store[name] = value
        return True
    async def delete(self, name, *args, **kwargs):
        if name in self.store:
            del self.store[name]
            return 1
        return 0
    async def incr(self, *args, **kwargs): return 1
    async def expire(self, *args, **kwargs): return True
    async def ping(self): return True
    async def aclose(self): pass

if os.environ.get("USE_MOCK_REDIS") == "true" or (os.environ.get("ENVIRONMENT") == "test" and not os.environ.get("REDIS_URL")):
    redis_client = MockRedis()
else:
    redis_client = Redis.from_url(
        settings.REDIS_URL, decode_responses=True, socket_timeout=5.0, socket_connect_timeout=5.0
    )

async def get_redis_client() -> AsyncGenerator[Redis, None]:
    try:
        yield redis_client  # type: ignore
    finally:
        pass
