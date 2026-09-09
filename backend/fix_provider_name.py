import asyncio

from sqlalchemy import text

from app.db.session import engine


async def fix():
    async with engine.begin() as conn:
        await conn.execute(text("UPDATE provider_mappings SET provider_name = 'yahoo' WHERE provider_name = 'YahooFinanceProvider'"))

if __name__ == "__main__":
    asyncio.run(fix())
