"""Market maintenance worker.

Responsibilities:
1. On startup: catch-up sync for instruments with 0 OHLCV rows (730 days).
2. Incremental daily sync: fetch from (max_date - 3 days) to today for existing instruments.
3. Idempotent UPSERT - safe to run multiple times.
4. Bounded concurrency - Semaphore(3) to be polite to Yahoo.
5. Runs in background; does NOT block API startup.

Usage (docker-compose service or manual):
    python -m app.scripts.market_maintenance
"""
from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select

from app.db.models import Instrument, OHLCVDaily, ProviderMapping
from app.db.session import async_session_maker
from app.market.registry import registry
from app.market.yahoo_provider import YahooFinanceProvider

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [market_maintenance] %(message)s",
)
logger = logging.getLogger(__name__)

_SEM = asyncio.Semaphore(3)  # max 3 concurrent Yahoo requests


async def _upsert_ohlcv(
    session_maker: object,
    inst_id: int,
    symbol: str,
    provider_symbol: str,
    start_date: datetime,
    end_date: datetime,
) -> int:
    """Fetch and upsert OHLCV rows. Returns number of rows inserted/updated."""
    async with _SEM:
        try:
            provider = registry.get_provider("yahoo")
            quotes = await asyncio.wait_for(
                provider.get_historical_quotes(
                    symbol=provider_symbol,
                    start_date=start_date,
                    end_date=end_date,
                ),
                timeout=30.0,
            )
        except TimeoutError:
            logger.warning(f"  Timeout fetching {symbol} ({provider_symbol})")
            return 0
        except Exception as e:
            logger.error(f"  Error fetching {symbol}: {e}")
            return 0

    if not quotes:
        logger.info(f"  No data returned for {symbol}")
        return 0

    records = [
        {
            "instrument_id": inst_id,
            "timestamp": q.timestamp,
            "open": q.open,
            "high": q.high,
            "low": q.low,
            "close": q.price,
            "volume": q.volume,
        }
        for q in quotes
    ]

    from sqlalchemy.dialects.postgresql import insert as pg_insert

    async with async_session_maker() as session:
        try:
            stmt = pg_insert(OHLCVDaily).values(records)
            stmt = stmt.on_conflict_do_update(
                constraint="uq_ohlcv_daily_instrument_time",
                set_={
                    "open": stmt.excluded.open,
                    "high": stmt.excluded.high,
                    "low": stmt.excluded.low,
                    "close": stmt.excluded.close,
                    "volume": stmt.excluded.volume,
                },
            )
            await session.execute(stmt)
            await session.commit()
            logger.info(f"  {symbol}: upserted {len(records)} rows")
            return len(records)
        except Exception as e:
            await session.rollback()
            logger.error(f"  DB upsert error for {symbol}: {e}")
            return 0


async def run_maintenance() -> None:
    """Main entry point. Safe to run repeatedly."""
    # Ensure Yahoo is registered
    yahoo = YahooFinanceProvider()
    registry.register(yahoo, is_primary=True)

    now = datetime.now(UTC)
    catchup_start = now - timedelta(days=730)  # 2 years

    logger.info("=== Market Maintenance Starting ===")
    logger.info(f"Time: {now.isoformat()}")

    async with async_session_maker() as session:
        # Load all active instruments with Yahoo mappings
        stmt = (
            select(
                Instrument.id,
                Instrument.symbol,
                ProviderMapping.provider_symbol,
            )
            .join(ProviderMapping, ProviderMapping.instrument_id == Instrument.id)
            .where(
                Instrument.is_active.is_(True),
                ProviderMapping.provider_name == "yahoo",
                ProviderMapping.is_primary.is_(True),
            )
            .order_by(Instrument.symbol)
        )
        result = await session.execute(stmt)
        instruments = result.all()

        # Get last OHLCV date per instrument
        count_stmt = select(
            OHLCVDaily.instrument_id,
            func.count(OHLCVDaily.id).label("row_count"),
            func.max(OHLCVDaily.timestamp).label("last_ts"),
        ).group_by(OHLCVDaily.instrument_id)
        count_result = await session.execute(count_stmt)
        ohlcv_info: dict[int, tuple[int, datetime | None]] = {
            row.instrument_id: (row.row_count, row.last_ts)
            for row in count_result
        }

    logger.info(f"Instruments to process: {len(instruments)}")

    catchup_tasks = []
    incremental_tasks = []

    for inst_id, symbol, provider_symbol in instruments:
        info = ohlcv_info.get(inst_id)
        if not info or info[0] == 0:
            # No history at all — full catch-up (730 days)
            logger.info(f"  [CATCHUP] {symbol}: 0 rows, fetching 730 days")
            catchup_tasks.append((inst_id, symbol, provider_symbol, catchup_start, now))
        else:
            row_count, last_ts = info
            if last_ts is not None and (now - last_ts).days >= 1:
                # Incremental: from (last_ts - 3 days) for safety overlap
                inc_start = last_ts - timedelta(days=3)
                logger.info(
                    f"  [INCREMENTAL] {symbol}: {row_count} rows, "
                    f"last={last_ts.date()}, fetching from {inc_start.date()}"
                )
                incremental_tasks.append((inst_id, symbol, provider_symbol, inc_start, now))
            else:
                logger.info(f"  [SKIP] {symbol}: {row_count} rows, up to date")

    total_catchup = len(catchup_tasks)
    total_incremental = len(incremental_tasks)
    logger.info(f"Catch-up: {total_catchup}, Incremental: {total_incremental}")

    # Process catch-up in batches of 5 to avoid overwhelming Yahoo
    success = 0
    batch_size = 5
    all_tasks = catchup_tasks + incremental_tasks

    for i in range(0, len(all_tasks), batch_size):
        batch = all_tasks[i : i + batch_size]
        results = await asyncio.gather(*[
            _upsert_ohlcv(async_session_maker, inst_id, sym, psym, sd, ed)
            for inst_id, sym, psym, sd, ed in batch
        ])
        success += sum(1 for r in results if r > 0)
        # Brief pause between batches to be Yahoo-respectful
        if i + batch_size < len(all_tasks):
            await asyncio.sleep(2.0)

    logger.info(
        f"=== Maintenance Complete: {success}/{len(all_tasks)} instruments updated ==="
    )


async def main_loop():
    import datetime
    try:
        from zoneinfo import ZoneInfo
    except ImportError:
        from backports.zoneinfo import ZoneInfo

    trt = ZoneInfo("Europe/Istanbul")

    # Run once on startup
    logger.info("Running initial market maintenance...")
    await run_maintenance()

    while True:
        now = datetime.datetime.now(trt)
        target = now.replace(hour=19, minute=0, second=0, microsecond=0)

        # If it's already past 19:00 today, schedule for tomorrow
        if now >= target:
            target += datetime.timedelta(days=1)

        wait_seconds = (target - now).total_seconds()
        logger.info(f"Sleeping for {wait_seconds:.0f} seconds until next maintenance window ({target.strftime('%Y-%m-%d %H:%M:%S %Z')})...")

        await asyncio.sleep(wait_seconds)

        logger.info("Starting scheduled market maintenance...")
        await run_maintenance()

if __name__ == "__main__":
    asyncio.run(main_loop())
