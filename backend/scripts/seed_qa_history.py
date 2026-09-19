import asyncio
import os
import sys
from datetime import UTC, datetime, timedelta
from decimal import Decimal

db_name = os.environ.get("POSTGRES_DB", "borsa_takip_test")
if "test" not in db_name.lower():
    sys.exit(1)
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("POSTGRES_DB", "borsa_takip_test")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import delete, select

from app.db.models import Instrument, OHLCVDaily
from app.db.session import async_session_maker


async def seed_history():
    async with async_session_maker() as session:
        res = await session.execute(select(Instrument))
        instruments = res.scalars().all()

        await session.execute(delete(OHLCVDaily))

        now = datetime.now(UTC)
        rows = []

        for inst in instruments:
            for i in range(250, -1, -1):
                dt = now - timedelta(days=i)
                day = 250 - i

                if day <= 50:
                    price = 50.0
                elif day <= 236:
                    price = 80.0
                else:
                    price = 85.0 if day % 2 == 0 else 81.0

                rows.append(OHLCVDaily(
                    instrument_id=inst.id,
                    timestamp=dt,
                    open=Decimal(str(round(price, 2))),
                    high=Decimal(str(round(price + 0.5, 2))),
                    low=Decimal(str(round(price - 0.5, 2))),
                    close=Decimal(str(round(price, 2))),
                    volume=1000000,
                    provider_name="yahoo"
                ))

        for i in range(0, len(rows), 10000):
            session.add_all(rows[i:i+10000])
            await session.commit()

        print(f"Inserted historical rows for {len(instruments)} instruments")

if __name__ == "__main__":
    asyncio.run(seed_history())
