from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import CalibrationCycle

async def freeze_calibration_cycle(
    db: AsyncSession, 
    cycle_id: int, 
    champion_hash: str, 
    challenger_manifest: str, 
    code_commit: str, 
    dataset_fingerprint: str
):
    res = await db.execute(select(CalibrationCycle).where(CalibrationCycle.id == cycle_id))
    cycle = res.scalars().first()
    if not cycle:
        raise ValueError("Cycle not found")
    if cycle.status != "OPEN":
        raise ValueError("Only OPEN cycles can be frozen")
    
    cycle.status = "FROZEN"
    cycle.champion_config_hash = champion_hash
    cycle.frozen_challenger_manifest_hash = challenger_manifest
    
    cycle.manifest_json = {
        "dataset_root_hash": dataset_fingerprint,
        "code_commit_sha": code_commit,
        "frozen_challenger_manifest_hash": challenger_manifest,
        "champion_config_hash": champion_hash,
        "metric_schema_version": "1.0.0",
        "execution_model_version": "1.0.0",
        "cost_model_version": "1.0.0",
        "decision_engine_version": "1.0.0",
        "lifecycle_policy_version": "1.0.0",
        "allocation_policy_version": "1.0.0",
        "trading_calendar_version": "1.0.0",
        "universe_fingerprint": dataset_fingerprint,
        "benchmark_fingerprint": dataset_fingerprint,
        "regime_definition_hash": "1.0.0",
        "promotion_guardrail_hash": "1.0.0"
    }
    
    cycle.locked_at = datetime.now(UTC)
    await db.commit()
    return cycle

async def consume_holdout(db: AsyncSession, cycle_id: int):
    res = await db.execute(select(CalibrationCycle).where(CalibrationCycle.id == cycle_id))
    cycle = res.scalars().first()
    if not cycle:
        raise ValueError("Cycle not found")
    if cycle.status != "FROZEN":
        raise ValueError("Only FROZEN cycles can consume holdout")
    
    cycle.status = "HOLDOUT_CONSUMED"
    cycle.holdout_consumed_at = datetime.now(UTC)
    await db.commit()
    return cycle
