import pytest
from app.db.models import CalibrationCycle
from app.services.governance import freeze_calibration_cycle, consume_holdout
from sqlalchemy.ext.asyncio import AsyncSession
import datetime
from app.db.session import async_session_maker

@pytest.mark.asyncio
async def test_calibration_cycle_state_transitions():
    async with async_session_maker() as db:
        # 1. Create OPEN
        cycle = CalibrationCycle(status="OPEN")
        db.add(cycle)
        await db.commit()
        await db.refresh(cycle)
        
        # 2. Consume holdout while OPEN should fail
        with pytest.raises(ValueError, match="Only FROZEN cycles can consume holdout"):
            await consume_holdout(db, cycle.id)
            
        # 3. Freeze
        frozen = await freeze_calibration_cycle(db, cycle.id, "champ_hash", "chall_hash", "commit", "dataset")
        assert frozen.status == "FROZEN"
        assert frozen.locked_at is not None
        
        # 4. Freeze again should fail
        with pytest.raises(ValueError, match="Only OPEN cycles can be frozen"):
            await freeze_calibration_cycle(db, cycle.id, "champ_hash2", "chall_hash2", "commit2", "dataset2")
            
        # 5. Consume holdout
        consumed = await consume_holdout(db, cycle.id)
        assert consumed.status == "HOLDOUT_CONSUMED"
        assert consumed.holdout_consumed_at is not None

        # 6. Consume again should fail
        with pytest.raises(ValueError, match="Only FROZEN cycles can consume holdout"):
            await consume_holdout(db, cycle.id)
