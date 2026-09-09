import asyncio
import csv
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Instrument, ProviderMapping
from app.db.session import engine


async def seed_bist100():
    csv_path = Path(__file__).parent.parent.parent.parent / "data" / "market" / "bist100_2026_Q3.csv"
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        return

    async with AsyncSession(engine) as session:
        # First safely rename old symbols to new symbols
        renames = {"IPEKE": "TRENJ", "KOZAA": "TRMET", "KOZAL": "TRALT"}
        for old_sym, new_sym in renames.items():
            old_inst = (await session.execute(select(Instrument).where(Instrument.symbol == old_sym))).scalar_one_or_none()
            if old_inst:
                old_inst.symbol = new_sym
                # Update provider mapping too
                mapping = (await session.execute(select(ProviderMapping).where(ProviderMapping.instrument_id == old_inst.id))).scalar_one_or_none()
                if mapping:
                    mapping.provider_symbol = f"{new_sym}.IS"
        await session.commit()

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            added = 0
            csv_symbols = set()
            for row in reader:
                symbol = row["symbol"]
                csv_symbols.add(symbol)

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
                    # Ensure active and updated symbol if needed
                    instrument.is_active = True

            # Deactivate any instruments that are NOT in the current BIST100 CSV but are marked active
            all_db_instruments = (await session.execute(select(Instrument).where(Instrument.is_active == True, Instrument.exchange == "BIST", Instrument.instrument_type == "STOCK"))).scalars().all()
            for db_inst in all_db_instruments:
                if db_inst.symbol not in csv_symbols:
                    db_inst.is_active = False

            await session.commit()
            print(f"Successfully seeded/updated {added} instruments from BIST100.")

if __name__ == "__main__":
    asyncio.run(seed_bist100())
