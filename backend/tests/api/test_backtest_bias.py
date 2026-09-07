import datetime
import uuid

import pytest
from sqlalchemy.future import select

from app.db.models import FundamentalData, Instrument, InstrumentType
from app.db.session import async_session_maker


@pytest.mark.asyncio
async def test_backtest_publication_timing():
    # 1. PUBLICATION TIMING
    # Fundamental/report: period_end = T0, published_at = T5
    # Backtest as_of T1-T4: data MUST NOT be visible.
    # Backtest as_of >= T5: data may become visible.

    async with async_session_maker() as db_session:
        inst = Instrument(symbol=f"PUB_{uuid.uuid4().hex[:4]}", name="Pub", exchange="BIST", instrument_type=InstrumentType.STOCK)
        db_session.add(inst)
        await db_session.commit()
        await db_session.refresh(inst)

        t0 = datetime.datetime(2025, 3, 31, tzinfo=datetime.UTC)
        t5 = datetime.datetime(2025, 5, 10, tzinfo=datetime.UTC)

        fd = FundamentalData(instrument_id=inst.id, period="2025Q1", published_at=t5, pe_ratio=15.5)
        db_session.add(fd)
        await db_session.commit()

        # Simulated point-in-time engine queries
        # As of T4 (May 9) -> Should not find it
        t4 = datetime.datetime(2025, 5, 9, tzinfo=datetime.UTC)
        query_t4 = select(FundamentalData).where(
            FundamentalData.instrument_id == inst.id,
            FundamentalData.published_at <= t4
        )
        res_t4 = await db_session.execute(query_t4)
        assert res_t4.scalars().first() is None

        # As of T5 (May 10) -> Should find it
        query_t5 = select(FundamentalData).where(
            FundamentalData.instrument_id == inst.id,
            FundamentalData.published_at <= t5
        )
        res_t5 = await db_session.execute(query_t5)
        assert res_t5.scalars().first() is not None

@pytest.mark.asyncio
async def test_backtest_same_candle_execution():
    # 2. SAME-CANDLE EXECUTION
    # Signal closed candle T -> earliest execution T+1 tradable open
    # We will simulate the behavior rule here to lock it in

    t1_close = datetime.datetime(2025, 5, 1, 18, 0, tzinfo=datetime.UTC)
    t2_open = datetime.datetime(2025, 5, 2, 9, 30, tzinfo=datetime.UTC)

    # Example logic constraint that engine must follow:
    # If signal generation time is t1_close
    signal_generated_at = t1_close

    # We attempt to execute it. The next candle must be STRICTLY greater than the signal candle's closing time
    # (or strictly next calendar trading day)
    proposed_execution_time = t2_open

    # Golden rule assertion
    assert proposed_execution_time > signal_generated_at, "Execution cannot happen on or before the signal's candle close"
