import asyncio
from datetime import datetime, timedelta, UTC
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import engine, async_session_maker
from app.db.models import Instrument, ProviderMapping, OHLCVDaily
from app.market.registry import registry
from app.market.yahoo_provider import YahooFinanceProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def sync_history(days: int = 365):
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
                quotes = await registry.get_provider("yahoo").get_historical_quotes(
                    symbol=provider_symbol,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if not quotes:
                    logger.warning(f"No history found for {symbol}")
                    continue
                
                await session.execute(
                    OHLCVDaily.__table__.delete().where(
                        OHLCVDaily.instrument_id == inst_id,
                        OHLCVDaily.timestamp >= start_date,
                        OHLCVDaily.timestamp <= end_date
                    )
                )
                
                new_records = []
                for q in quotes:
                    new_records.append(
                        OHLCVDaily(
                            instrument_id=inst_id,
                            timestamp=q.timestamp,
                            open=q.open,
                            high=q.high,
                            low=q.low,
                            close=q.price,
                            volume=q.volume
                        )
                    )
                
                if new_records:
                    session.add_all(new_records)
                    await session.commit()
                    success_count += 1
                    logger.info(f"Inserted {len(new_records)} days for {symbol}")
                
            except Exception as e:
                logger.error(f"Failed to sync {symbol}: {e}")
                await session.rollback()
                
            # Sleep slightly to avoid rate limit
            await asyncio.sleep(0.5)

        logger.info(f"Sync complete. Success: {success_count}/{len(instruments)}")

if __name__ == "__main__":
    asyncio.run(sync_history())
