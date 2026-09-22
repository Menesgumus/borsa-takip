import asyncio
from sqlalchemy.future import select
from sqlalchemy import func
from app.db.session import engine_dev
from app.db.models import Instrument, OHLCVDaily, FundamentalData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

async_session_dev = sessionmaker(
    engine_dev, class_=AsyncSession, expire_on_commit=False
)

async def check_dev_db():
    async with async_session_dev() as db:
        res = await db.execute(select(func.count(Instrument.id)))
        inst_count = res.scalar()
        
        res = await db.execute(select(func.count(OHLCVDaily.id)))
        ohlcv_count = res.scalar()

        res = await db.execute(select(func.min(OHLCVDaily.timestamp), func.max(OHLCVDaily.timestamp)))
        ohlcv_range = res.first()

        res = await db.execute(select(func.count(FundamentalData.id)))
        fund_count = res.scalar()

        print(f"DEV DB Instruments: {inst_count}")
        print(f"DEV DB OHLCV: {ohlcv_count} (Range: {ohlcv_range})")
        print(f"DEV DB Fundamentals: {fund_count}")

asyncio.run(check_dev_db())
