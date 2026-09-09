import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


async def check():
    engine = create_async_engine(str(settings.database_url))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(text("SELECT id, symbol, is_active FROM instruments"))
        rows = result.fetchall()
        print("Instruments:", rows)

        txs = await session.execute(text("SELECT COUNT(*) FROM portfolio_transactions"))
        print("Tx count:", txs.scalar())

        decisions = await session.execute(text("SELECT COUNT(*) FROM decision_snapshots"))
        print("Decision count:", decisions.scalar())

if __name__ == "__main__":
    asyncio.run(check())
