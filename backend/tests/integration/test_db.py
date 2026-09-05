import pytest
from sqlalchemy import text
from app.db.session import engine, async_session_maker

@pytest.mark.asyncio
async def test_postgres_connection() -> None:
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        row = result.scalar()
        assert row == 1

@pytest.mark.asyncio
async def test_session_rollback() -> None:
    async with async_session_maker() as session:
        # Just creating a session to ensure it can open and rollback properly
        pass
    # Without errors, it commits and closes.
