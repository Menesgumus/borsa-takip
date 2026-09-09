import asyncio
import yfinance as yf
from sqlalchemy import select
from app.db.session import async_session_maker
from app.db.models import Instrument

async def main():
    async with async_session_maker() as session:
        res = await session.execute(select(Instrument))
        instruments = res.scalars().all()
        for inst in instruments:
            if inst.name == inst.symbol:
                try:
                    ticker = yf.Ticker(inst.symbol + ".IS")
                    long_name = ticker.info.get('longName') or ticker.info.get('shortName')
                    if long_name:
                        inst.name = long_name
                        print(f"Updated {inst.symbol} to {long_name}")
                except Exception as e:
                    pass
        await session.commit()

asyncio.run(main())
