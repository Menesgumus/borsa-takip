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


@pytest.mark.asyncio
async def test_frozen_manifest_version_fields():
    """
    Verify that the frozen calibration manifest contains:
    - decision_engine_version matching the authoritative ENGINE_VERSION constant
    - lifecycle_policy_version matching the authoritative LIFECYCLE_POLICY_VERSION constant
    - code_commit_sha matching the exact supplied value
    - No invented version strings (v1_stub, v1_strict, v1_equal, v2_canonical, v1_bist)
    """
    from app.services.decision_engine import ENGINE_VERSION as DECISION_ENGINE_VERSION
    from app.services.lifecycle_engine import LIFECYCLE_POLICY_VERSION
    from app.services.stage8_manifest import get_champion_hash, get_challenger_manifest_hash

    FAKE_CODE_SHA = "aabbccdd" * 8  # 64-char fake but deterministic

    async with async_session_maker() as db:
        cycle = CalibrationCycle(status="OPEN")
        db.add(cycle)
        await db.commit()
        await db.refresh(cycle)

        frozen = await freeze_calibration_cycle(
            db,
            cycle.id,
            champion_hash=get_champion_hash(),
            challenger_manifest=get_challenger_manifest_hash(),
            code_commit=FAKE_CODE_SHA,
            dataset_fingerprint="test_dataset_fingerprint",
        )

        manifest = frozen.manifest_json
        assert isinstance(manifest, dict), "manifest_json must be a dict, not a string"

        # Real version constants must be present
        assert manifest["decision_engine_version"] == DECISION_ENGINE_VERSION, (
            f"decision_engine_version mismatch: got {manifest['decision_engine_version']!r}, "
            f"expected {DECISION_ENGINE_VERSION!r}"
        )
        assert manifest["lifecycle_policy_version"] == LIFECYCLE_POLICY_VERSION, (
            f"lifecycle_policy_version mismatch: got {manifest['lifecycle_policy_version']!r}, "
            f"expected {LIFECYCLE_POLICY_VERSION!r}"
        )

        # Exact code SHA must be stored
        assert manifest["code_commit_sha"] == FAKE_CODE_SHA, (
            f"code_commit_sha mismatch: got {manifest['code_commit_sha']!r}"
        )

        # No invented version labels
        invented_labels = {"v1_stub", "v1_strict", "v1_equal", "v2_canonical", "v1_bist", "v1_static", "v1_event_safe"}
        for key, val in manifest.items():
            assert val not in invented_labels, (
                f"Invented version label found: {key}={val!r}. "
                "Use real constants or NOT_IMPLEMENTED/UNVERSIONED."
            )


@pytest.mark.asyncio
async def test_frozen_manifest_hash_distinctness():
    """
    Verify that champion_config_hash, challenger_manifest_hash, and
    calibration_manifest_hash are all distinct non-empty values.
    """
    from app.services.stage8_manifest import get_champion_hash, get_challenger_manifest_hash

    async with async_session_maker() as db:
        cycle = CalibrationCycle(status="OPEN")
        db.add(cycle)
        await db.commit()
        await db.refresh(cycle)

        champ_hash = get_champion_hash()
        chal_hash  = get_challenger_manifest_hash()

        frozen = await freeze_calibration_cycle(
            db,
            cycle.id,
            champion_hash=champ_hash,
            challenger_manifest=chal_hash,
            code_commit="deadbeef" * 8,
            dataset_fingerprint="test_fp",
        )

        calibration_manifest_hash = frozen.manifest_hash

        assert champ_hash, "champion_config_hash must not be empty"
        assert chal_hash,  "challenger_manifest_hash must not be empty"
        assert calibration_manifest_hash, "calibration_manifest_hash must not be empty"

        assert champ_hash != chal_hash, (
            "champion_config_hash and challenger_manifest_hash must differ"
        )
        assert champ_hash != calibration_manifest_hash, (
            "champion_config_hash and calibration_manifest_hash must differ"
        )
        assert chal_hash != calibration_manifest_hash, (
            "challenger_manifest_hash and calibration_manifest_hash must differ"
        )

        # Determinism: same inputs must produce same hashes
        cycle2 = CalibrationCycle(status="OPEN")
        db.add(cycle2)
        await db.commit()
        await db.refresh(cycle2)

        frozen2 = await freeze_calibration_cycle(
            db,
            cycle2.id,
            champion_hash=champ_hash,
            challenger_manifest=chal_hash,
            code_commit="deadbeef" * 8,
            dataset_fingerprint="test_fp",
        )
        assert frozen2.manifest_hash == calibration_manifest_hash, (
            "calibration_manifest_hash must be deterministic for identical inputs"
        )

