import asyncio
from sqlalchemy import select
from app.db.session import async_session_maker
from app.db.models import Instrument, ProviderMapping

async def verify_bist100():
    async with async_session_maker() as session:
        instruments = (await session.execute(select(Instrument).where(Instrument.is_active == True))).scalars().all()
        mappings = (await session.execute(select(ProviderMapping))).scalars().all()
        
        symbols = set(i.symbol for i in instruments)
        mapped_symbols = set(m.instrument_id for m in mappings if m.provider_name == 'yahoo')
        resolved_count = len([i for i in instruments if i.id in mapped_symbols])
        
        print("expected constituents: 100")
        print(f"seeded active constituents: {len(instruments)}")
        print(f"unique symbols: {len(symbols)}")
        print(f"provider mappings resolved: {resolved_count}")
        print(f"unresolved: {len(instruments) - resolved_count}")

if __name__ == "__main__":
    asyncio.run(verify_bist100())
