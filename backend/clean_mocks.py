import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings

async def clean():
    engine = create_async_engine(str(settings.database_url))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        await session.execute(text("DELETE FROM provider_mappings"))
        await session.execute(text("DELETE FROM instruments"))
        await session.commit()
        print("Cleared mocks")

if __name__ == "__main__":
    asyncio.run(clean())
