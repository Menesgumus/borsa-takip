"""Seed deterministic QA instruments in borsa_takip_test.

Usage:
    POSTGRES_DB=borsa_takip_test uv run python scripts/seed_qa_instruments.py

This script is idempotent — safe to run multiple times.
It ONLY targets borsa_takip_test (fails if pointed elsewhere).
Production/dev databases are never touched.
"""

from __future__ import annotations

import asyncio
import os
import sys

# Guard: refuse to seed non-test databases
db_name = os.environ.get("POSTGRES_DB", "borsa_takip_test")
if "test" not in db_name.lower():
    print(f"ERROR: refusing to seed non-test database: {db_name}", file=sys.stderr)
    sys.exit(1)

# Ensure environment is set before importing app modules
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("POSTGRES_DB", "borsa_takip_test")

# Add parent to path so app imports work from scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select  # noqa: E402

from app.db.models import Instrument, InstrumentType, ProviderMapping  # noqa: E402
from app.db.session import async_session_maker  # noqa: E402

# Deterministic QA instrument definitions
# These are used exclusively by the E2E test suite with the mock provider
QA_INSTRUMENTS = [
    {"symbol": "AEFES", "name": "Anadolu Efes Biracilik", "exchange": "BIST"},
    {"symbol": "THYAO", "name": "Türk Hava Yolları", "exchange": "BIST"},
    {"symbol": "GARAN", "name": "Garanti Bankası", "exchange": "BIST"},
    {"symbol": "ASELS", "name": "Aselsan Elektronik", "exchange": "BIST"},
    {"symbol": "SISE",  "name": "Şişecam Şirketleri", "exchange": "BIST"},
]


async def seed() -> None:
    async with async_session_maker() as session:
        seeded = 0
        skipped = 0

        for inst_data in QA_INSTRUMENTS:
            symbol = inst_data["symbol"]

            # Check if instrument already exists
            existing = await session.execute(
                select(Instrument).where(Instrument.symbol == symbol)
            )
            instrument = existing.scalar_one_or_none()

            if instrument is None:
                instrument = Instrument(
                    symbol=symbol,
                    name=inst_data["name"],
                    exchange=inst_data["exchange"],
                    instrument_type=InstrumentType.STOCK,
                    is_active=True,
                )
                session.add(instrument)
                await session.flush()  # get the assigned id
                print(f"  + Created instrument: {symbol} (id={instrument.id})")
                seeded += 1
            else:
                print(f"  - Skipped existing: {symbol} (id={instrument.id})")
                skipped += 1

            # Ensure mock provider mapping exists
            existing_mapping = await session.execute(
                select(ProviderMapping).where(
                    ProviderMapping.instrument_id == instrument.id,
                    ProviderMapping.provider_name == "mock",
                )
            )
            mapping = existing_mapping.scalar_one_or_none()

            if mapping is None:
                mapping = ProviderMapping(
                    instrument_id=instrument.id,
                    provider_name="mock",
                    provider_symbol=symbol,
                    is_primary=True,
                    priority=1,
                )
                session.add(mapping)
                print(f"    + Created mock provider mapping for {symbol}")
            else:
                print(f"    - Existing mock mapping for {symbol}")

        await session.commit()
        print(f"\nDone. Seeded={seeded}, Skipped={skipped}")


if __name__ == "__main__":
    asyncio.run(seed())
