import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Instrument, OHLCVDaily
from app.market.registry import registry

logger = logging.getLogger(__name__)


async def fetch_and_store_history(
    db: AsyncSession, symbol: str, start_date: datetime, end_date: datetime
) -> int:
    """Fetch history for an instrument and upsert into OHLCVDaily."""
    # 1. Resolve instrument
    result = await db.execute(
        select(Instrument).where(Instrument.symbol == symbol, Instrument.is_active.is_(True))
    )
    instrument = result.scalar_one_or_none()
    if not instrument:
        raise ValueError(f"Instrument not found or inactive: {symbol}")

    # 2. Get provider mapping
    # Just use primary mapping if exists, else fallback to mock/symbol
    await db.refresh(instrument, ["provider_mappings"])
    provider_name = "mock"
    provider_symbol = str(instrument.symbol)

    if instrument.provider_mappings:
        mapping = next(
            (m for m in instrument.provider_mappings if m.is_primary),
            instrument.provider_mappings[0],
        )
        provider_name = mapping.provider_name
        provider_symbol = str(mapping.provider_symbol)

    # 3. Fetch from provider
    provider = registry.get_provider(provider_name)
    quotes = await provider.get_historical_quotes(provider_symbol, start_date, end_date)

    if not quotes:
        return 0

    # 4. Upsert into DB
    records = []
    for q in quotes:
        # OHLC Validation
        if q.high < q.open or q.high < q.price or q.high < q.low:
            logger.warning(f"Invalid high for {symbol} at {q.timestamp}")
            continue
        if q.low > q.open or q.low > q.price or q.low > q.high:
            logger.warning(f"Invalid low for {symbol} at {q.timestamp}")
            continue
        if q.price < 0 or q.open < 0 or q.high < 0 or q.low < 0:
            logger.warning(f"Negative price for {symbol} at {q.timestamp}")
            continue

        records.append(
            {
                "instrument_id": instrument.id,
                "timestamp": q.timestamp,
                "open": q.open,
                "high": q.high,
                "low": q.low,
                "close": q.price,
                "volume": q.volume,
                "provider_name": q.source_name,
            }
        )

    if not records:
        return 0

    stmt = insert(OHLCVDaily).values(records)

    # On conflict, update the values
    update_dict = {
        "open": stmt.excluded.open,
        "high": stmt.excluded.high,
        "low": stmt.excluded.low,
        "close": stmt.excluded.close,
        "volume": stmt.excluded.volume,
        "provider_name": stmt.excluded.provider_name,
        "updated_at": datetime.now(UTC),
    }

    stmt = stmt.on_conflict_do_update(constraint="uq_ohlcv_daily_instrument_time", set_=update_dict)

    result = await db.execute(stmt)
    await db.commit()
    return len(records)
