"""Seed real US and Gold instruments into the database.

Usage:
    uv run python scripts/seed_real_instruments.py

This script is idempotent.
"""

from __future__ import annotations

import asyncio
import os
import sys

# Add parent to path so app imports work from scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select

from app.db.models import AssetClass, Instrument, InstrumentType, ProviderMapping
from app.db.session import async_session_maker

US_EQUITIES = [
    {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "asset_class": AssetClass.US_EQUITY, "currency": "USD"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ", "asset_class": AssetClass.US_EQUITY, "currency": "USD"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ", "asset_class": AssetClass.US_EQUITY, "currency": "USD"},
    {"symbol": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ", "asset_class": AssetClass.US_EQUITY, "currency": "USD"},
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ", "asset_class": AssetClass.US_EQUITY, "currency": "USD"},
    {"symbol": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ", "asset_class": AssetClass.US_EQUITY, "currency": "USD"},
    {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ", "asset_class": AssetClass.US_EQUITY, "currency": "USD"},
    {"symbol": "BRK-B", "name": "Berkshire Hathaway Inc.", "exchange": "NYSE", "asset_class": AssetClass.US_EQUITY, "currency": "USD"},
    {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "exchange": "NYSE", "asset_class": AssetClass.US_EQUITY, "currency": "USD"},
    {"symbol": "JNJ", "name": "Johnson & Johnson", "exchange": "NYSE", "asset_class": AssetClass.US_EQUITY, "currency": "USD"},
]

GOLD = [
    {"symbol": "GLDTR.IS", "name": "QNB Finans Portfoy Altin ETF", "exchange": "BIST", "asset_class": AssetClass.GOLD, "currency": "TRY"},
]

FX_REFERENCE = [
    {"symbol": "USDTRY=X", "name": "USD/TRY Exchange Rate", "exchange": "CCY", "asset_class": AssetClass.FX_REFERENCE, "currency": "TRY"},
]

async def seed() -> None:
    async with async_session_maker() as session:
        print("Starting seed process...")
        for data in US_EQUITIES + GOLD + FX_REFERENCE:
            symbol = data["symbol"]
            inst = await session.scalar(select(Instrument).where(Instrument.symbol == symbol))

            if not inst:
                print(f"Creating {symbol}...")
                itype = InstrumentType.STOCK
                if data["asset_class"] == AssetClass.GOLD:
                    itype = InstrumentType.ETF
                elif data["asset_class"] == AssetClass.FX_REFERENCE:
                    itype = InstrumentType.CURRENCY

                inst = Instrument(
                    symbol=symbol,
                    name=data["name"],
                    exchange=data["exchange"],
                    instrument_type=itype,
                    is_active=True,
                    asset_class=data["asset_class"],
                    currency=data["currency"]
                )
                session.add(inst)
                await session.flush()
            else:
                print(f"Updating {symbol}...")
                inst.name = data["name"]
                inst.asset_class = data["asset_class"]
                inst.currency = data["currency"]
                inst.is_active = True

            pm = await session.scalar(
                select(ProviderMapping)
                .where(ProviderMapping.instrument_id == inst.id)
                .where(ProviderMapping.provider_name == "yahoo")
            )

            if not pm:
                print(f"Adding yahoo ProviderMapping for {symbol}...")
                pm = ProviderMapping(
                    instrument_id=inst.id,
                    provider_name="yahoo",
                    provider_symbol=symbol,
                    is_primary=True
                )
                session.add(pm)

        await session.commit()
        print("Seed complete.")

if __name__ == "__main__":
    asyncio.run(seed())
