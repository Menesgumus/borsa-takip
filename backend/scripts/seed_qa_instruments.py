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
from datetime import UTC, datetime, timedelta
from decimal import Decimal

# Guard: refuse to seed non-test databases
db_name = os.environ.get("POSTGRES_DB", "borsa_takip_test")
if "test" not in db_name.lower() and "qa" not in db_name.lower():
    print(f"ERROR: refusing to seed non-test database: {db_name}", file=sys.stderr)
    sys.exit(1)

# Ensure environment is set before importing app modules
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("POSTGRES_DB", "borsa_takip_test")

# Add parent to path so app imports work from scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import delete, select, update  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Instrument, InstrumentType, ProviderMapping, OHLCVDaily, FundamentalData  # noqa: E402
from app.db.session import async_session_maker  # noqa: E402
from app.market.mock_provider import MockMarketDataProvider
from app.core.redis import get_redis_client

QA_INSTRUMENTS = [
    {"symbol": "AEFES", "name": "Anadolu Efes Biracilik", "exchange": "BIST"},
    {"symbol": "THYAO", "name": "TǬrk Hava Yollar", "exchange": "BIST"},
    {"symbol": "GARAN", "name": "Garanti Bankas", "exchange": "BIST"},
    {"symbol": "ASELS", "name": "Aselsan Elektronik", "exchange": "BIST"},
    {"symbol": "SISE",  "name": "?iYecam ?irketleri", "exchange": "BIST"},
    # The dedicated QA Deterministic Buy Fixture
    {"symbol": "QABUY", "name": "QA Deterministic Buy Fixture", "exchange": "QA"},
]

async def seed_qabuy_technical_data(session: AsyncSession, instrument_id: int):
    # Fetch deterministic quote from MockMarketDataProvider
    provider = MockMarketDataProvider()
    quote = await provider.get_quote("QABUY")
    fixture_price = quote.price
    volume = quote.volume
    
    # Generate 250 sequential daily candles to satisfy scanner (SMA200 requires >= 200)
    # Ensure they form a clean bullish trend/stable behavior
    # We use stable price = fixture_price, with slight variations
    now = datetime.now(UTC)
    start_date = (now - timedelta(days=250)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    await session.execute(delete(OHLCVDaily).where(OHLCVDaily.instrument_id == instrument_id))
    
    candles = []
    # Create an uptrend to guarantee STRONG_BUY from MACD and RSI and SMA
    # For day i in 0..249: price goes from fixture_price * 0.5 up to fixture_price
    for i in range(250):
        trend_factor = Decimal("0.5") + (Decimal("0.5") * Decimal(i) / Decimal(249))
        day_price = fixture_price * trend_factor
        
        # for the final day, make it equal to fixture price
        if i == 249:
            day_price = fixture_price

        candles.append(OHLCVDaily(
            instrument_id=instrument_id,
            timestamp=start_date + timedelta(days=i),
            open=day_price * Decimal("0.99"),
            high=day_price * Decimal("1.01"),
            low=day_price * Decimal("0.98"),
            close=day_price,
            volume=volume,
            provider_name="mock"
        ))
    
    session.add_all(candles)

async def seed_qabuy_fundamental_data(session: AsyncSession, instrument_id: int):
    await session.execute(delete(FundamentalData).where(FundamentalData.instrument_id == instrument_id))
    
    # Strong fundamentals: PE < 15, PB < 2.0
    fund = FundamentalData(
        instrument_id=instrument_id,
        period="2026Q1",
        pe_ratio=Decimal("10.0"),
        pb_ratio=Decimal("1.5"),
        market_cap=Decimal("10000000000.0"),
        net_income=Decimal("1000000000.0"),
        revenue=Decimal("5000000000.0"),
        source="mock",
        published_at=datetime.now(UTC)
    )
    session.add(fund)

async def seed() -> None:
    async with async_session_maker() as session:
        for inst_data in QA_INSTRUMENTS:
            symbol = inst_data["symbol"]

            existing = await session.execute(select(Instrument).where(Instrument.symbol == symbol))
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
                await session.flush()
                print(f"  + Created instrument: {symbol} (id={instrument.id})")
            
            # Ensure mock provider mapping is primary
            # And demote any other mappings
            mappings_result = await session.execute(
                select(ProviderMapping).where(ProviderMapping.instrument_id == instrument.id)
            )
            mappings = mappings_result.scalars().all()
            
            mock_mapping = next((m for m in mappings if m.provider_name == "mock"), None)
            
            # Demote others
            for m in mappings:
                if m.provider_name != "mock" and m.is_primary:
                    m.is_primary = False
                    session.add(m)
            
            if mock_mapping is None:
                mock_mapping = ProviderMapping(
                    instrument_id=instrument.id,
                    provider_name="mock",
                    provider_symbol=symbol,
                    is_primary=True,
                    priority=1,
                )
                session.add(mock_mapping)
                print(f"    + Created mock provider mapping for {symbol}")
            else:
                if not mock_mapping.is_primary:
                    mock_mapping.is_primary = True
                    session.add(mock_mapping)
                print(f"    - Existing mock mapping for {symbol} verified as primary")
            
            if symbol == "QABUY":
                await seed_qabuy_technical_data(session, instrument.id)
                await seed_qabuy_fundamental_data(session, instrument.id)
                print(f"    + Seeded deterministic technical and fundamental data for QABUY")

        await session.commit()
        print("Database seeded.")
        
    # Clear QA Redis opportunities cache
    redis_gen = get_redis_client()
    redis = await anext(redis_gen)
    keys = await redis.keys("opportunities:market:*")
    if keys:
        await redis.delete(*keys)
        print(f"Deleted {len(keys)} QA Redis opportunity cache keys.")
    else:
        print("No QA Redis opportunity cache keys found.")
    await redis.aclose()


if __name__ == "__main__":
    asyncio.run(seed())
