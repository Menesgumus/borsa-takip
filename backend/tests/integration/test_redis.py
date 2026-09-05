import pytest
from app.core.redis import redis_client

@pytest.mark.asyncio
async def test_redis_ping() -> None:
    # Test bounded ping
    assert await redis_client.ping()

@pytest.mark.asyncio
async def test_redis_scoped_key_cleanup() -> None:
    # Test test namespace
    test_key = "test_namespace:test_key"
    await redis_client.set(test_key, "value", ex=10) # scoped TTL
    val = await redis_client.get(test_key)
    assert val == "value"
    
    # Cleanup
    await redis_client.delete(test_key)
    val = await redis_client.get(test_key)
    assert val is None
