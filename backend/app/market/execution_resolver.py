from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import TradingSession, OHLCVDaily

class ExecutionResolver:
    @staticmethod
    async def resolve_d_plus_one_execution(
        db: AsyncSession,
        instrument_id: int,
        signal_date: date,
        calendar_name: str = "BIST"
    ) -> float | str:
        """
        Resolves D+1 execution logic.
        signal uses completed D information.
        Finds official next BIST trading session after D.
        Requires actual instrument RAW OPEN for that session.
        Returns:
            price (float) if execution is valid
            "NON_EVALUABLE" if the session exists but price is missing
            "NO_FUTURE_SESSION" if dataset ends
        """
        from datetime import timedelta
        
        # 1. Find next official trading session after D
        stmt = (
            select(TradingSession)
            .where(TradingSession.calendar_name == calendar_name)
            .where(TradingSession.session_date > signal_date)
            .where(TradingSession.is_trading_day == True)
            .order_by(TradingSession.session_date.asc())
            .limit(1)
        )
        result = await db.execute(stmt)
        next_session = result.scalars().first()
        
        if not next_session:
            return "NO_FUTURE_SESSION"
            
        # 2. Require actual instrument RAW OPEN for that session
        stmt2 = (
            select(OHLCVDaily)
            .where(OHLCVDaily.instrument_id == instrument_id)
            .where(OHLCVDaily.timestamp >= next_session.session_date)
            .where(OHLCVDaily.timestamp < next_session.session_date + timedelta(days=1))
        )
        result2 = await db.execute(stmt2)
        ohlcv = result2.scalars().first()
        
        if not ohlcv or ohlcv.open is None:
            return "NON_EVALUABLE"
            
        return float(ohlcv.open)
