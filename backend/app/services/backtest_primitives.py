from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import asc, desc

from app.db.models import OHLCVDaily, FundamentalData

class MissingDataException(Exception):
    pass

async def get_execution_price(db: AsyncSession, instrument_id: int, signal_date: datetime):
    """
    Returns the valid execution price for a signal generated using data strictly <= signal_date.
    The rule is: Execution D+1 OPEN.
    We look for the FIRST available trading session OPEN strictly > signal_date.
    """
    # Force timezone awareness for comparison
    if signal_date.tzinfo is None:
        signal_date = signal_date.replace(tzinfo=UTC)

    res = await db.execute(
        select(OHLCVDaily)
        .where(
            OHLCVDaily.instrument_id == instrument_id,
            OHLCVDaily.timestamp > signal_date
        )
        .order_by(asc(OHLCVDaily.timestamp))
        .limit(1)
    )
    bar = res.scalars().first()
    
    if not bar:
        raise MissingDataException("No future trading session available for execution.")
        
    return {
        "execution_price": float(bar.open),
        "execution_timestamp": bar.timestamp
    }

async def get_point_in_time_fundamentals(db: AsyncSession, instrument_id: int, as_of_date: datetime):
    """
    Returns the most recent fundamental data actually published and available
    to the system on or before the as_of_date.
    """
    if as_of_date.tzinfo is None:
        as_of_date = as_of_date.replace(tzinfo=UTC)

    # We must use published_at or available_at, NOT period_end!
    res = await db.execute(
        select(FundamentalData)
        .where(
            FundamentalData.instrument_id == instrument_id,
            FundamentalData.published_at <= as_of_date
        )
        .order_by(desc(FundamentalData.published_at))
        .limit(1)
    )
    return res.scalars().first()

async def get_point_in_time_technicals(db: AsyncSession, instrument_id: int, as_of_date: datetime, limit: int = 100):
    """
    Fetches technical bars strictly <= as_of_date to prevent future leakage.
    """
    if as_of_date.tzinfo is None:
        as_of_date = as_of_date.replace(tzinfo=UTC)

    res = await db.execute(
        select(OHLCVDaily)
        .where(
            OHLCVDaily.instrument_id == instrument_id,
            OHLCVDaily.timestamp <= as_of_date
        )
        .order_by(desc(OHLCVDaily.timestamp))
        .limit(limit)
    )
    # Return chronologically sorted
    bars = res.scalars().all()
    return list(reversed(bars))

def evaluate_decision_safe(instrument_id: int, tech_bars: list, fund: FundamentalData):
    """
    Example primitive wrapper that prevents fabrication if required data is missing.
    """
    if not tech_bars:
        return "NO_ACTION_DATA"
        
    # Example logic using the data
    last_close = float(tech_bars[-1].close)
    
    if fund is None or fund.pe_ratio is None:
        return "NO_ACTION_DATA" # Fundamental required
        
    if float(fund.pe_ratio) < 15 and last_close > 10:
        return "BUY"
    return "HOLD"
