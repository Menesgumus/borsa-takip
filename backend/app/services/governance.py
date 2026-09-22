import hashlib
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import CalibrationCycle
from app.services.canonical import get_canonical_json

async def update_calibration_config(db: AsyncSession, cycle_id: int, updates: dict):
    """
    Canonical service API for configuring the CalibrationCycle.
    Configuration fields can ONLY be prepared when OPEN.
    Once FROZEN or HOLDOUT_CONSUMED, config is immutable.
    """
    res = await db.execute(select(CalibrationCycle).where(CalibrationCycle.id == cycle_id))
    cycle = res.scalars().first()
    if not cycle:
        raise ValueError("Cycle not found")
        
    if cycle.status != "OPEN":
        raise ValueError(f"Cannot mutate configuration of {cycle.status} cycle")

    if "champion_config_hash" in updates:
        cycle.champion_config_hash = updates["champion_config_hash"]
    if "frozen_challenger_manifest_hash" in updates:
        cycle.frozen_challenger_manifest_hash = updates["frozen_challenger_manifest_hash"]
        
    # other fields...
    await db.commit()
    return cycle

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
    
    # Real canonical manifest object
    manifest = {
        "dataset_root_hash": dataset_fingerprint,
        "code_commit_sha": code_commit,
        "frozen_challenger_manifest_hash": challenger_manifest,
        "champion_config_hash": champion_hash,
        "metric_schema_version": "v2_canonical",
        "execution_model_version": "v1_event_safe",
        "cost_model_version": "v1_static",
        "decision_engine_version": "v1_stub",
        "lifecycle_policy_version": "v1_strict",
        "allocation_policy_version": "v1_equal",
        "trading_calendar_version": "v1_bist",
        "universe_fingerprint": "LIMITED_BY_DATA",
        "benchmark_fingerprint": "LIMITED_BY_DATA",
        "regime_definition_hash": "LIMITED_BY_DATA",
        "promotion_guardrail_hash": "v1_strict",
        "train_interval_start": cycle.train_interval_start.isoformat() if cycle.train_interval_start else "UNAVAILABLE",
        "train_interval_end": cycle.train_interval_end.isoformat() if cycle.train_interval_end else "UNAVAILABLE",
        "validation_interval_start": cycle.validation_interval_start.isoformat() if cycle.validation_interval_start else "UNAVAILABLE",
        "validation_interval_end": cycle.validation_interval_end.isoformat() if cycle.validation_interval_end else "UNAVAILABLE",
        "holdout_interval_start": cycle.holdout_interval_start.isoformat() if cycle.holdout_interval_start else "UNAVAILABLE",
        "holdout_interval_end": cycle.holdout_interval_end.isoformat() if cycle.holdout_interval_end else "UNAVAILABLE",
    }
    
    canon_str = get_canonical_json(manifest)
    manifest_hash = hashlib.sha256(canon_str.encode("utf-8")).hexdigest()
    
    cycle.manifest_json = manifest
    cycle.manifest_hash = manifest_hash
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
