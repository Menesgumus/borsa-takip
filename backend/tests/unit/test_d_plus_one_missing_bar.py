import pytest
from datetime import date, datetime, UTC
from app.market.execution_resolver import ExecutionResolver
from app.db.models import TradingSession, OHLCVDaily, Instrument
from app.db.session import async_session_maker

@pytest.mark.asyncio
async def test_d_plus_one_execution_semantics():
    async with async_session_maker() as db_session:
        # Create test instrument
        import uuid
        test_symbol = f"TESTBIST_{uuid.uuid4().hex[:8]}"
        inst = Instrument(symbol=test_symbol, name="Test", exchange="BIST", asset_class="BIST_EQUITY", is_active=True)
        db_session.add(inst)
        
        # Setup trading sessions
        # D = Monday (signal), D+1 = Tuesday (missing bar), D+2 = Wed (has bar)
        sess_mon = TradingSession(calendar_name="BIST", session_date=date(2025, 1, 6), is_trading_day=True, session_type="REGULAR")
        sess_tue = TradingSession(calendar_name="BIST", session_date=date(2025, 1, 7), is_trading_day=True, session_type="REGULAR")
        sess_wed = TradingSession(calendar_name="BIST", session_date=date(2025, 1, 8), is_trading_day=True, session_type="REGULAR")
        
        db_session.add_all([sess_mon, sess_tue, sess_wed])
        await db_session.commit()
        await db_session.refresh(inst)
        
        # 1. Missing execution bar
        # Signal on Monday, Tuesday is OPEN but no OHLCV exists
        result = await ExecutionResolver.resolve_d_plus_one_execution(db_session, inst.id, date(2025, 1, 6))
        assert result == "NON_EVALUABLE"
        
        # 2. Add bar for Tuesday
        ohlcv_tue = OHLCVDaily(
            instrument_id=inst.id,
            timestamp=datetime(2025, 1, 7, tzinfo=UTC),
            open=100.5, high=101, low=100, close=100.8, volume=1000,
            provider_name="mock", is_adjusted=False, session_type="REGULAR"
        )
        db_session.add(ohlcv_tue)
        await db_session.commit()
        
        result2 = await ExecutionResolver.resolve_d_plus_one_execution(db_session, inst.id, date(2025, 1, 6))
        assert result2 == 100.5
        
        # 3. Holiday behavior
        # Make Tuesday a holiday
        sess_tue.is_trading_day = False
        sess_tue.session_type = "CLOSED_HOLIDAY"
        await db_session.commit()
        
        # Signal Monday -> looks for next session -> Wednesday
        # Wed has no bar -> NON_EVALUABLE
        result3 = await ExecutionResolver.resolve_d_plus_one_execution(db_session, inst.id, date(2025, 1, 6))
        assert result3 == "NON_EVALUABLE"
        
        # Add bar for Wed
        ohlcv_wed = OHLCVDaily(
            instrument_id=inst.id,
            timestamp=datetime(2025, 1, 8, tzinfo=UTC),
            open=102.0, high=103, low=101, close=102.5, volume=1000,
            provider_name="mock", is_adjusted=False, session_type="REGULAR"
        )
        db_session.add(ohlcv_wed)
        await db_session.commit()
        
        result4 = await ExecutionResolver.resolve_d_plus_one_execution(db_session, inst.id, date(2025, 1, 6))
        assert result4 == 102.0
