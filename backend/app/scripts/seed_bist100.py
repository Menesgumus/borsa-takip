import asyncio
import csv
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import engine
from app.db.models import Instrument, ProviderMapping

async def seed_bist100():
    csv_path = Path(__file__).parent.parent.parent.parent / "data" / "market" / "bist100_2024.csv"
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        return

    async with AsyncSession(engine) as session:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            added = 0
            for row in reader:
                symbol = row["symbol"]
                
                # Check if instrument exists
                stmt = select(Instrument).where(Instrument.symbol == symbol)
                result = await session.execute(stmt)
                instrument = result.scalar_one_or_none()
                
                if not instrument:
                    instrument = Instrument(
                        symbol=symbol,
                        name=row["name"],
                        exchange=row["exchange"],
                        instrument_type=row["instrument_type"],
                        is_active=True
                    )
                    session.add(instrument)
                    await session.flush()  # to get ID
                    
                    # Add provider mapping
                    mapping = ProviderMapping(
                        instrument_id=instrument.id,
                        provider_name="yahoo",
                        provider_symbol=row["provider_symbol"],
                        is_primary=True
                    )
                    session.add(mapping)
                    added += 1
                else:
                    # Ensure active
                    instrument.is_active = True

            await session.commit()
            print(f"Successfully seeded/updated {added} instruments from BIST100.")

if __name__ == "__main__":
    asyncio.run(seed_bist100())
