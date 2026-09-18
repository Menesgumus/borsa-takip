import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.db.models import Instrument, InstrumentType, OHLCVDaily
from app.db.session import async_session_maker
from app.services.scanner_technical import get_batched_technical_inputs


@pytest.mark.asyncio
async def test_get_batched_technical_inputs_query_count():
    async with async_session_maker() as db:
        # Create symbols
        s1 = f"TECH1_{uuid.uuid4().hex[:4]}"
        s2 = f"TECH2_{uuid.uuid4().hex[:4]}"

        i1 = Instrument(symbol=s1, name="T1", exchange="BIST", instrument_type=InstrumentType.STOCK)
        i2 = Instrument(symbol=s2, name="T2", exchange="BIST", instrument_type=InstrumentType.STOCK)
        db.add_all([i1, i2])
        await db.commit()
        await db.refresh(i1)
        await db.refresh(i2)

        # Add 300 rows for i1, 100 rows for i2
        now = datetime.now(UTC)
        rows = []
        for i in range(300):
            rows.append(OHLCVDaily(
                instrument_id=i1.id,
                timestamp=now - timedelta(days=i),
                open=Decimal("100"), high=Decimal("105"), low=Decimal("95"), close=Decimal("100"), volume=1000
            ))
        for i in range(100):
            rows.append(OHLCVDaily(
                instrument_id=i2.id,
                timestamp=now - timedelta(days=i),
                open=Decimal("50"), high=Decimal("55"), low=Decimal("45"), close=Decimal("50"), volume=1000
            ))
        db.add_all(rows)
        await db.commit()

        # We can't easily assert exactly one query without mocking the session execute,
        # but we can patch db.execute to count queries, or just ensure the output is exactly bounded
        from unittest.mock import patch

        original_execute = db.execute
        query_count = 0

        async def mock_execute(*args, **kwargs):
            nonlocal query_count
            query_count += 1
            return await original_execute(*args, **kwargs)

        with patch.object(db, 'execute', side_effect=mock_execute):
            result = await get_batched_technical_inputs(db, [s1, s2])

        # 1 query for Instruments, 1 query for batched OHLCVDaily (subquery + join)
        assert query_count == 2

        assert s1 in result
        assert s2 in result

        t1 = result[s1]
        t2 = result[s2]

        assert t1 is not None
        assert t2 is not None

        # i1 had 300 rows. The batch should limit to 250 rows.
        # SMA 200 should be available since 250 >= 200
        assert t1.sma_200 is not None
        assert t1.sma_50 is not None

        # i2 had 100 rows.
        # SMA 200 should be None since 100 < 200
        assert t2.sma_200 is None
        assert t2.sma_50 is not None
