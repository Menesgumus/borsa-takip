import asyncio
import os
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.insert(0, str(Path('.').resolve()))

async def main():
    from app.core.config import settings
    print("Effective Settings:")
    print(f"ENVIRONMENT: {settings.ENVIRONMENT}")
    print(f"POSTGRES_HOST: {settings.POSTGRES_HOST}")
    print(f"POSTGRES_PORT: {settings.POSTGRES_PORT}")
    print(f"POSTGRES_DB: {settings.POSTGRES_DB}")
    print(f"REDIS_URL: {settings.REDIS_URL}")
    print(f"MOCK MARKET: {settings.ENABLE_MOCK_MARKET_DATA}")

    engine = create_async_engine(str(settings.database_url))
    async with engine.connect() as conn:
        res = await conn.execute(text('SELECT current_database()'))
        db_name = res.scalar()
        print(f"current_database(): {db_name}")

    await engine.dispose()

if __name__ == '__main__':
    os.environ["ENVIRONMENT"] = "test"
    os.environ["POSTGRES_DB"] = "borsa_takip_test"
    os.environ.setdefault("POSTGRES_HOST", "127.0.0.1")
    os.environ.setdefault("POSTGRES_PORT", "5434")
    os.environ.setdefault("POSTGRES_USER", "qa_user")
    os.environ.setdefault("POSTGRES_PASSWORD", "qa_password")
    os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:6381/0")
    os.environ.setdefault("ENABLE_MOCK_MARKET_DATA", "true")

    asyncio.run(main())
