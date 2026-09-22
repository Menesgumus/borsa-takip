import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Instrument, OHLCVDaily, FundamentalData, InstrumentType
from app.services.dataset_hashing import get_dataset_fingerprint
import uuid
import asyncio

from app.db.session import async_session_maker

@pytest.mark.asyncio
async def test_dataset_hashing_properties():
    async with async_session_maker() as db:
        # 1. Setup base instrument and data
        inst_symbol = f"TEST_{uuid.uuid4().hex[:4]}"
        inst1 = Instrument(symbol=inst_symbol, name="Test", exchange="BIST", instrument_type=InstrumentType.STOCK)
        db.add(inst1)
        await db.commit()
        await db.refresh(inst1)
        
        t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
        
        b0 = OHLCVDaily(instrument_id=inst1.id, timestamp=t0, open=100, high=105, low=95, close=102, volume=1000)
        fund = FundamentalData(instrument_id=inst1.id, period="2025Q4", published_at=t0, pe_ratio=10.5)
        db.add_all([b0, fund])
        await db.commit()
        
        hash_base = await get_dataset_fingerprint(db, [inst1.id])
        
        # 2. Same data, different DB row ID
        await db.delete(b0)
        await db.delete(fund)
        await db.delete(inst1)
        await db.commit()
        
        inst2 = Instrument(symbol=inst_symbol, name="Test", exchange="BIST", instrument_type=InstrumentType.STOCK)
        db.add(inst2)
        await db.commit()
        await db.refresh(inst2)
        
        b0_copy = OHLCVDaily(instrument_id=inst2.id, timestamp=t0, open=100, high=105, low=95, close=102, volume=1000)
        fund_copy = FundamentalData(instrument_id=inst2.id, period="2025Q4", published_at=t0, pe_ratio=10.5)
        db.add_all([b0_copy, fund_copy])
        await db.commit()
        
        hash_copy = await get_dataset_fingerprint(db, [inst2.id])
        assert hash_base == hash_copy, "Different DB row ID must yield same dataset hash"
        
        # 3. Change close price -> different hash
        b0_copy.close = 103
        await db.commit()
        hash_close_changed = await get_dataset_fingerprint(db, [inst2.id])
        assert hash_close_changed != hash_base, "Changed close price must yield different hash"
        
        # Reset
        b0_copy.close = 102
        await db.commit()
        
        # 4. Change volume -> different hash
        b0_copy.volume = 1001
        await db.commit()
        hash_vol_changed = await get_dataset_fingerprint(db, [inst2.id])
        assert hash_vol_changed != hash_base, "Changed volume must yield different hash"
        
        b0_copy.volume = 1000
        await db.commit()
        
        # 5. published_at changes -> different hash
        fund_copy.published_at = datetime(2026, 1, 2, tzinfo=timezone.utc)
        await db.commit()
        hash_pub_changed = await get_dataset_fingerprint(db, [inst2.id])
        assert hash_pub_changed != hash_base, "Changed published_at must yield different hash"
        
        fund_copy.published_at = t0
        await db.commit()
        
        # 6. available_at changes -> different hash
        fund_copy.available_at = t0
        await db.commit()
        hash_avail_changed = await get_dataset_fingerprint(db, [inst2.id])
        assert hash_avail_changed != hash_base, "Changed available_at must yield different hash"
        
        fund_copy.available_at = None
        await db.commit()
        
        # 7. Fundamental value changes -> different hash
        fund_copy.pe_ratio = 11.0
        await db.commit()
        hash_pe_changed = await get_dataset_fingerprint(db, [inst2.id])
        assert hash_pe_changed != hash_base, "Changed fundamental value must yield different hash"
        
        # 8. Schema version changes -> different hash
        fund_copy.pe_ratio = 10.5
        await db.commit()
        hash_schema_changed = await get_dataset_fingerprint(db, [inst2.id], schema_version_override="2.0.0")
        assert hash_schema_changed != hash_base, "Schema version change must yield different hash"
        
        # 9. Insertion order changes -> identical hash
        await db.delete(b0_copy)
        await db.delete(fund_copy)
        await db.commit()
        
        # Insert them in reverse order
        fund_new = FundamentalData(instrument_id=inst2.id, period="2025Q4", published_at=t0, pe_ratio=10.5)
        db.add(fund_new)
        await db.commit()
        
        b0_new = OHLCVDaily(instrument_id=inst2.id, timestamp=t0, open=100, high=105, low=95, close=102, volume=1000)
        db.add(b0_new)
        await db.commit()
        
        hash_reordered = await get_dataset_fingerprint(db, [inst2.id])
        assert hash_reordered == hash_base, "Different insertion order must yield identical hash"
