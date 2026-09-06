import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.db.models import Instrument
from app.db.session import async_session_maker
from app.market.history import fetch_and_store_history

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_ingestion():
    end_date = datetime.now(UTC)
    start_date = end_date - timedelta(days=365)  # 1 year by default

    async with async_session_maker() as db:
        result = await db.execute(select(Instrument).where(Instrument.is_active.is_(True)))
        instruments = result.scalars().all()

        for inst in instruments:
            logger.info(f"Ingesting historical data for {inst.symbol}...")
            try:
                count = await fetch_and_store_history(db, inst.symbol, start_date, end_date)
                logger.info(f"Stored {count} records for {inst.symbol}.")
            except Exception as e:
                logger.error(f"Error fetching data for {inst.symbol}: {e}")


if __name__ == "__main__":
    asyncio.run(run_ingestion())
