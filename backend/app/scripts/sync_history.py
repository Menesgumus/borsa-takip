import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.db.models import Instrument, OHLCVDaily, ProviderMapping
from app.db.session import async_session_maker
from app.market.registry import registry
from app.market.yahoo_provider import YahooFinanceProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def sync_history(days: int = 730):
    # Ensure Yahoo provider is registered
    yahoo = YahooFinanceProvider()
    registry.register(yahoo, is_primary=True)

    end_date = datetime.now(UTC)
    start_date = end_date - timedelta(days=days)

    async with async_session_maker() as session:
        # Get active instruments with Yahoo mapping
        stmt = (
            select(Instrument.id, Instrument.symbol, ProviderMapping.provider_symbol)
            .join(ProviderMapping)
            .where(Instrument.is_active == True)
            .where(ProviderMapping.provider_name == "yahoo")
        )
        result = await session.execute(stmt)
        instruments = result.all()

        logger.info(f"Found {len(instruments)} instruments to sync history for.")

        success_count = 0
        for inst_id, symbol, provider_symbol in instruments:
            logger.info(f"Syncing history for {symbol} via {provider_symbol}...")
            try:
                # We now fetch 2 years of history to ensure we have ~500 trading bars for SMA200+ math
                quotes = await registry.get_provider("yahoo").get_historical_quotes(
                    symbol=provider_symbol,
                    start_date=start_date,
                    end_date=end_date
                )

                if not quotes:
                    logger.warning(f"No history found for {symbol}")
                    continue

                new_records = []
                for q in quotes:
                    new_records.append({
                        "instrument_id": inst_id,
                        "timestamp": q.timestamp,
                        "open": q.open,
                        "high": q.high,
                        "low": q.low,
                        "close": q.price,
                        "volume": q.volume
                    })
                from sqlalchemy.dialects.postgresql import insert as pg_insert

                if new_records:
                    stmt = pg_insert(OHLCVDaily).values(new_records)
                    stmt = stmt.on_conflict_do_update(
                        constraint='uq_ohlcv_daily_instrument_time',
                        set_={
                            'open': stmt.excluded.open,
                            'high': stmt.excluded.high,
                            'low': stmt.excluded.low,
                            'close': stmt.excluded.close,
                            'volume': stmt.excluded.volume,
                        }
                    )
                    await session.execute(stmt)
                    await session.commit()
                    success_count += 1
                    logger.info(f"Inserted/Updated {len(new_records)} days for {symbol}")

            except Exception as e:
                logger.error(f"Failed to sync {symbol}: {e}")
                await session.rollback()

            # Sleep slightly to avoid rate limit
            await asyncio.sleep(0.5)

        logger.info(f"Sync complete. Success: {success_count}/{len(instruments)}")

if __name__ == "__main__":
    asyncio.run(sync_history())
