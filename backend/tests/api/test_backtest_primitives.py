import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Instrument, OHLCVDaily, FundamentalData, InstrumentType
from app.services.backtest_primitives import (
    get_execution_price,
    get_point_in_time_fundamentals,
    get_point_in_time_technicals,
    evaluate_decision_safe,
    MissingDataException
)
import uuid

from app.db.session import async_session_maker

@pytest.mark.asyncio
async def test_event_safe_signal_timing():
    async with async_session_maker() as db:
        inst = Instrument(symbol=f"TEST_{uuid.uuid4().hex[:4]}", name="Test", exchange="BIST", instrument_type=InstrumentType.STOCK)
        db.add(inst)
        await db.commit()
        await db.refresh(inst)

        d0 = datetime(2026, 1, 1, 15, 0, tzinfo=timezone.utc)
        d1 = datetime(2026, 1, 2, 15, 0, tzinfo=timezone.utc)
        d2 = datetime(2026, 1, 5, 15, 0, tzinfo=timezone.utc) # Weekend skipped (3,4)

        b0 = OHLCVDaily(instrument_id=inst.id, timestamp=d0, open=100, high=105, low=95, close=102, volume=1000)
        b1 = OHLCVDaily(instrument_id=inst.id, timestamp=d1, open=102, high=106, low=100, close=105, volume=1000)
        b2 = OHLCVDaily(instrument_id=inst.id, timestamp=d2, open=110, high=115, low=108, close=112, volume=1000)
        
        db.add_all([b0, b1, b2])
        await db.commit()

        # Signal generated exactly at D1 (using D1 close)
        signal_date = d1

        # Execution must happen at D2 open
        exec_info = await get_execution_price(db, inst.id, signal_date)
        
        # Must execute at 110 (D2 OPEN), not D1 open (102) or close (105)
        assert exec_info["execution_price"] == 110.0
        assert exec_info["execution_timestamp"] == d2

@pytest.mark.asyncio
async def test_future_row_appended_invisible_at_d():
    async with async_session_maker() as db:
        inst = Instrument(symbol=f"TEST_{uuid.uuid4().hex[:4]}", name="Test", exchange="BIST", instrument_type=InstrumentType.STOCK)
        db.add(inst)
        await db.commit()
        await db.refresh(inst)

        d0 = datetime(2026, 1, 1, 15, 0, tzinfo=timezone.utc)
        b0 = OHLCVDaily(instrument_id=inst.id, timestamp=d0, open=10, high=15, low=9, close=12, volume=1000)
        
        fund = FundamentalData(instrument_id=inst.id, period="2025Q4", period_end=datetime(2025, 12, 31, tzinfo=timezone.utc), published_at=datetime(2025, 12, 31, tzinfo=timezone.utc), pe_ratio=10)
        
        db.add_all([b0, fund])
        await db.commit()

        # Evaluate at D0
        techs_before = await get_point_in_time_technicals(db, inst.id, d0)
        funds_before = await get_point_in_time_fundamentals(db, inst.id, d0)
        dec_before = evaluate_decision_safe(inst.id, techs_before, funds_before)

        # Append future data with extreme values
        d1 = datetime(2026, 1, 2, 15, 0, tzinfo=timezone.utc)
        d2 = datetime(2026, 1, 3, 15, 0, tzinfo=timezone.utc)
        b1 = OHLCVDaily(instrument_id=inst.id, timestamp=d1, open=999, high=999, low=999, close=999, volume=999)
        b2 = OHLCVDaily(instrument_id=inst.id, timestamp=d2, open=999, high=999, low=999, close=999, volume=999)
        db.add_all([b1, b2])
        await db.commit()

        # Evaluate at D0 again
        techs_after = await get_point_in_time_technicals(db, inst.id, d0)
        funds_after = await get_point_in_time_fundamentals(db, inst.id, d0)
        dec_after = evaluate_decision_safe(inst.id, techs_after, funds_after)

        assert len(techs_before) == 1
        assert len(techs_after) == 1
        assert dec_before == dec_after

@pytest.mark.asyncio
async def test_fundamental_publication_timing():
    async with async_session_maker() as db:
        inst = Instrument(symbol=f"TEST_{uuid.uuid4().hex[:4]}", name="Test", exchange="BIST", instrument_type=InstrumentType.STOCK)
        db.add(inst)
        await db.commit()
        await db.refresh(inst)

        # Period ended T0, published T5
        t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
        t5 = datetime(2026, 1, 6, tzinfo=timezone.utc)
        
        fund = FundamentalData(
            instrument_id=inst.id, 
            period="2025Q4", 
            period_end=t0, 
            published_at=t5, 
            pe_ratio=12
        )
        db.add(fund)
        await db.commit()

        t4 = datetime(2026, 1, 5, tzinfo=timezone.utc)
        t6 = datetime(2026, 1, 7, tzinfo=timezone.utc)

        # as_of T4 -> fundamental unavailable
        fund_t4 = await get_point_in_time_fundamentals(db, inst.id, t4)
        assert fund_t4 is None

        # as_of T5 or later -> available
        fund_t6 = await get_point_in_time_fundamentals(db, inst.id, t6)
        assert fund_t6 is not None
        assert float(fund_t6.pe_ratio) == 12.0

@pytest.mark.asyncio
async def test_stale_missing_data_not_fabricated():
    async with async_session_maker() as db:
        inst = Instrument(symbol=f"TEST_{uuid.uuid4().hex[:4]}", name="Test", exchange="BIST", instrument_type=InstrumentType.STOCK)
        db.add(inst)
        await db.commit()
        await db.refresh(inst)

        d0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
        
        # Provide technicals, but missing fundamentals
        b0 = OHLCVDaily(instrument_id=inst.id, timestamp=d0, open=10, high=15, low=9, close=12, volume=1000)
        db.add(b0)
        await db.commit()

        techs = await get_point_in_time_technicals(db, inst.id, d0)
        funds = await get_point_in_time_fundamentals(db, inst.id, d0)

        assert len(techs) == 1
        assert funds is None

        dec = evaluate_decision_safe(inst.id, techs, funds)
        
        # Missing required input must produce NO_ACTION_DATA (not BUY/SELL)
        assert dec == "NO_ACTION_DATA"
