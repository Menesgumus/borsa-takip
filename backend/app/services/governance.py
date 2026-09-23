import hashlib
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import CalibrationCycle
from app.services.canonical import get_canonical_json

# Import real authoritative version constants from their canonical modules.
# Do NOT invent version labels here — use what the actual code declares.
from app.services.decision_engine import ENGINE_VERSION as DECISION_ENGINE_VERSION
from app.services.lifecycle_engine import LIFECYCLE_POLICY_VERSION


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

    await db.commit()
    return cycle


async def freeze_calibration_cycle(
    db: AsyncSession,
    cycle_id: int,
    champion_hash: str,
    challenger_manifest: str,
    code_commit: str,
    dataset_fingerprint: str,
):
    """
    Freeze the cycle through the canonical governance path.
    Sets status, manifest_json, manifest_hash, and locked_at.
    No caller may mutate status or manifest fields directly after this.
    """
    res = await db.execute(select(CalibrationCycle).where(CalibrationCycle.id == cycle_id))
    cycle = res.scalars().first()
    if not cycle:
        raise ValueError("Cycle not found")
    if cycle.status != "OPEN":
        raise ValueError("Only OPEN cycles can be frozen")

    cycle.status = "FROZEN"
    cycle.champion_config_hash = champion_hash
    cycle.frozen_challenger_manifest_hash = challenger_manifest

    # ─── Canonical calibration manifest ───────────────────────────────────────
    # Version fields:
    #   - decision_engine_version: imported from app.services.decision_engine (authoritative)
    #   - lifecycle_policy_version: imported from app.services.lifecycle_engine (authoritative)
    #   - All other sub-systems that have no real versioned implementation are
    #     explicitly labelled NOT_IMPLEMENTED or UNVERSIONED so they cannot be
    #     mistaken for real controlled artefacts.
    manifest = {
        # Hashes
        "champion_config_hash":           champion_hash,
        "frozen_challenger_manifest_hash": challenger_manifest,
        "dataset_root_hash":              dataset_fingerprint,
        "code_commit_sha":                code_commit,

        # Real version constants from authoritative modules
        "decision_engine_version":        DECISION_ENGINE_VERSION,
        "lifecycle_policy_version":       LIFECYCLE_POLICY_VERSION,

        # Sub-systems without a real versioned implementation
        "execution_model_version":        "NOT_IMPLEMENTED",
        "cost_model_version":             "NOT_IMPLEMENTED",
        "allocation_policy_version":      "NOT_IMPLEMENTED",
        "trading_calendar_version":       "NOT_IMPLEMENTED",
        "metric_schema_version":          "NOT_IMPLEMENTED",
        "promotion_guardrail_version":    "NOT_IMPLEMENTED",

        # Data/universe limitations
        "universe_fingerprint":           "LIMITED_BY_DATA",
        "benchmark_fingerprint":          "LIMITED_BY_DATA",
        "regime_definition_hash":         "LIMITED_BY_DATA",

        # Interval coverage
        "train_interval_start":  cycle.train_interval_start.isoformat() if cycle.train_interval_start else "UNAVAILABLE",
        "train_interval_end":    cycle.train_interval_end.isoformat()   if cycle.train_interval_end   else "UNAVAILABLE",
        "validation_interval_start": cycle.validation_interval_start.isoformat() if cycle.validation_interval_start else "UNAVAILABLE",
        "validation_interval_end":   cycle.validation_interval_end.isoformat()   if cycle.validation_interval_end   else "UNAVAILABLE",
        "holdout_interval_start": cycle.holdout_interval_start.isoformat() if cycle.holdout_interval_start else "UNAVAILABLE",
        "holdout_interval_end":   cycle.holdout_interval_end.isoformat()   if cycle.holdout_interval_end   else "UNAVAILABLE",
    }

    canon_str    = get_canonical_json(manifest)
    manifest_hash = hashlib.sha256(canon_str.encode("utf-8")).hexdigest()

    cycle.manifest_json  = manifest
    cycle.manifest_hash  = manifest_hash
    cycle.locked_at      = datetime.now(UTC)

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
