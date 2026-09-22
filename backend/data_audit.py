import asyncio
from sqlalchemy.future import select
from sqlalchemy import func
from app.db.session import async_session_maker
from app.db.models import Instrument, OHLCVDaily, FundamentalData

async def run_audit():
    async with async_session_maker() as db:
        res = await db.execute(select(func.count(Instrument.id)))
        inst_count = res.scalar()
        
        res = await db.execute(select(func.count(OHLCVDaily.id)))
        ohlcv_count = res.scalar()

        res = await db.execute(select(func.min(OHLCVDaily.timestamp), func.max(OHLCVDaily.timestamp)))
        ohlcv_range = res.first()

        res = await db.execute(select(func.count(FundamentalData.id)))
        fund_count = res.scalar()

        print(f"Instruments: {inst_count}")
        print(f"OHLCV: {ohlcv_count} (Range: {ohlcv_range})")
        print(f"Fundamentals: {fund_count}")

asyncio.run(run_audit())
