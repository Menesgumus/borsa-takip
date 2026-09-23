import asyncio
from datetime import date
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.db.session import async_session_maker
from app.db.models import TradingSession
from app.market.trading_calendar import is_trading_day, get_session_type
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_calendar():
    start_year = 2020
    end_year = 2026
    
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    
    calendar_name = "BIST"
    
    async with async_session_maker() as db:
        # Generate days
        values = []
        current = start_date
        while current <= end_date:
            from datetime import timedelta
            is_open = is_trading_day(current, calendar_name)
            sess_type = get_session_type(current, calendar_name)
            values.append({
                "calendar_name": calendar_name,
                "session_date": current,
                "is_trading_day": is_open,
                "session_type": sess_type
            })
            current += timedelta(days=1)
            
        # Bulk upsert
        stmt = insert(TradingSession).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["calendar_name", "session_date"],
            set_={
                "is_trading_day": stmt.excluded.is_trading_day,
                "session_type": stmt.excluded.session_type
            }
        )
        
        await db.execute(stmt)
        await db.commit()
        
        logger.info(f"Seeded trading calendar for {calendar_name} from {start_date} to {end_date}")

if __name__ == "__main__":
    asyncio.run(seed_calendar())
