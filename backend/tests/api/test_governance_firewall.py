import pytest
from app.db.models import CalibrationCycle
from app.services.governance import freeze_calibration_cycle, consume_holdout, update_calibration_config
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
            
        # 3. Can mutate config while OPEN
        cycle = await update_calibration_config(db, cycle.id, {"champion_config_hash": "pre_champ"})
        assert cycle.champion_config_hash == "pre_champ"
            
        # 4. Freeze
        frozen = await freeze_calibration_cycle(db, cycle.id, "champ_hash", "chall_hash", "commit", "dataset")
        assert frozen.status == "FROZEN"
        assert frozen.locked_at is not None
        assert frozen.manifest_hash is not None
        assert frozen.manifest_json["champion_config_hash"] == "champ_hash"
        
        # 5. Freeze again should fail
        with pytest.raises(ValueError, match="Only OPEN cycles can be frozen"):
            await freeze_calibration_cycle(db, cycle.id, "champ_hash2", "chall_hash2", "commit2", "dataset2")
            
        # 6. Mutate config while FROZEN should fail
        with pytest.raises(ValueError, match="Cannot mutate configuration of FROZEN cycle"):
            await update_calibration_config(db, cycle.id, {"champion_config_hash": "evil"})
            
        # 7. Consume holdout
        consumed = await consume_holdout(db, cycle.id)
        assert consumed.status == "HOLDOUT_CONSUMED"
        assert consumed.holdout_consumed_at is not None

        # 8. Mutate config while HOLDOUT_CONSUMED should fail
        with pytest.raises(ValueError, match="Cannot mutate configuration of HOLDOUT_CONSUMED cycle"):
            await update_calibration_config(db, cycle.id, {"dataset_root_hash": "evil"})

        # 9. Consume again should fail
        with pytest.raises(ValueError, match="Only FROZEN cycles can consume holdout"):
            await consume_holdout(db, cycle.id)
