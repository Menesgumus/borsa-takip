import asyncio
import logging
from datetime import UTC, datetime, timedelta
from app.db.session import async_session_maker
from app.db.models import Instrument, ProviderMapping
from sqlalchemy import select
from app.market.historical_ohlcv_ingestor import ingest_ohlcv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_ingestion():
    # By default, ingest 5 years of history
    end_date = datetime.now(UTC)
    start_date = end_date - timedelta(days=5*365)
    
    async with async_session_maker() as db:
        # Get all active BIST equities with Yahoo mapping
        result = await db.execute(
            select(Instrument.symbol)
            .join(ProviderMapping)
            .where(
                Instrument.is_active == True,
                Instrument.asset_class == "BIST_EQUITY",
                ProviderMapping.provider_name == "yahoo"
            )
        )
        symbols = list(result.scalars().all())
        
        if not symbols:
            logger.error("No active BIST equities with Yahoo mapping found.")
            return

        logger.info(f"Starting ingestion for {len(symbols)} symbols from {start_date.date()} to {end_date.date()}")
        run_id = await ingest_ohlcv(
            db=db,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            provider_name="yahoo",
            dataset_type="OHLCV",
            concurrency=5
        )
        logger.info(f"Ingestion completed with run ID: {run_id}")

if __name__ == "__main__":
    asyncio.run(run_ingestion())
