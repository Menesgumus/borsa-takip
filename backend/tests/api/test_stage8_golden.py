import pytest
from decimal import Decimal
from datetime import datetime, timezone

from app.db.models import Instrument, Portfolio, User, InstrumentType, LifecycleHealthState, LifecycleAction, DecisionAction
from app.services.lifecycle_engine import process_position_lifecycle
from app.schemas.decision import DecisionResult
from app.services.stage8_manifest import generate_challenger_manifest, CHAMPION_CONFIG
from app.db.session import async_session_maker
import uuid

def create_mock_decision(view: str, data_score: int = 100) -> DecisionResult:
    return DecisionResult(
        instrument_id=1,
        horizon="MEDIUM",
        market_view=DecisionAction(view),
        as_of=datetime.now(timezone.utc),
        overall_market_score=Decimal("50"),
        confidence_score=Decimal("0.9"),
        data_quality_score=Decimal(str(data_score)),
        reason_codes=[],
        warnings=[],
        missing_data=False,
        engine_version="v2.0"
    )

async def simulate_sequence(db, portfolio_id: int, instrument_id: int, sequence: list, policy_overrides: dict):
    # sequence is list of (market_view, quantity, weight, max_limit, market_key, is_evaluable)
    # returns list of resulting health_state, recommended_action, counters
    results = []
    for step in sequence:
        view, qty, wt, limit, key, ev = step
        decision = create_mock_decision(view)
        
        lc = await process_position_lifecycle(
            db=db,
            portfolio_id=portfolio_id,
            instrument_id=instrument_id,
            current_quantity=Decimal(str(qty)),
            current_weight=Decimal(str(wt)),
            max_concentration_limit=Decimal(str(limit)),
            decision=decision,
            market_key=key,
            context_key_partial=key,
            is_evaluable=ev,
            policy_overrides=policy_overrides
        )
        # Flush so next step reads updated
        await db.flush()
        
        results.append({
            "health": lc.health_state,
            "action": lc.recommended_action,
            "neg_count": lc.negative_confirmation_count,
            "rec_count": lc.recovery_confirmation_count,
            "add_count": lc.add_confirmation_count,
            "strong_sell_count": lc.strong_sell_confirmation_count
        })
    return results

@pytest.mark.asyncio
async def test_stage8_golden_sequences():
    async with async_session_maker() as db:
        # Create base entities
        user = User(email=f"test_{uuid.uuid4()}@a.com", password_hash="a")
        inst = Instrument(symbol=f"GOLDEN_{uuid.uuid4().hex[:4]}", name="G", exchange="X", instrument_type=InstrumentType.STOCK)
        db.add_all([user, inst])
        await db.commit()
        await db.refresh(user)
        await db.refresh(inst)
        
        port = Portfolio(user_id=user.id, name="Golden")
        db.add(port)
        await db.commit()
        await db.refresh(port)
        
        manifest = generate_challenger_manifest()
        # Add champion to the list for testing
        candidates = [{"candidate_id": "CHAMPION"}] + manifest
        
        for cand in candidates:
            # Build overrides
            overrides = dict(CHAMPION_CONFIG)
            if "changed_parameter" in cand:
                overrides[cand["changed_parameter"]] = cand["challenger_value"]
                
            p_id = port.id
            i_id = inst.id
            
            # --- Test 1: Stable repeated BUY ---
            # Using unique keys per iteration to simulate time advancing
            seq1 = [
                ("BUY", 10, 0.1, 0.3, f"k1_{cand['candidate_id']}", True),
                ("BUY", 10, 0.1, 0.3, f"k2_{cand['candidate_id']}", True),
                ("BUY", 10, 0.1, 0.3, f"k3_{cand['candidate_id']}", True),
            ]
            r1 = await simulate_sequence(db, p_id, i_id, seq1, overrides)
            assert r1[-1]["health"] == LifecycleHealthState.STABLE
            
            # Check ADD eligibility:
            # CHAMPION needs 2 BUYs. k2 and k3 are the 2 BUYs. (k1 initializes STABLE, wait k1 is a BUY so add=1. k2 BUY -> add=2)
            # cand ADD_3 needs 3.
            add_thresh = overrides["ADD_THRESHOLD"]
            if r1[-1]["add_count"] >= add_thresh:
                assert r1[-1]["action"] == LifecycleAction.CONSIDER_ADD
            
            # Reset by closing
            await simulate_sequence(db, p_id, i_id, [("HOLD", 0, 0, 0, f"close1_{cand['candidate_id']}", True)], overrides)

            # --- Test 2: Five negatives (EXIT) ---
            seq2 = [
                ("HOLD", 10, 0.1, 0.3, f"k_h_{cand['candidate_id']}", True), # Re-enter
                ("SELL", 10, 0.1, 0.3, f"k_s1_{cand['candidate_id']}", True),
                ("SELL", 10, 0.1, 0.3, f"k_s2_{cand['candidate_id']}", True),
                ("SELL", 10, 0.1, 0.3, f"k_s3_{cand['candidate_id']}", True),
                ("SELL", 10, 0.1, 0.3, f"k_s4_{cand['candidate_id']}", True),
                ("SELL", 10, 0.1, 0.3, f"k_s5_{cand['candidate_id']}", True),
                ("SELL", 10, 0.1, 0.3, f"k_s6_{cand['candidate_id']}", True),
            ]
            r2 = await simulate_sequence(db, p_id, i_id, seq2, overrides)
            
            exit_thresh = overrides["EXIT_THRESHOLD"]
            # After 'exit_thresh' negatives (plus 1 for the initialization step, wait k_h is HOLD, neg=0)
            # s1: neg=1, s2: neg=2 ... 
            assert r2[exit_thresh]["action"] == LifecycleAction.CONSIDER_EXIT
            
            await simulate_sequence(db, p_id, i_id, [("HOLD", 0, 0, 0, f"close2_{cand['candidate_id']}", True)], overrides)

            # --- Test 3: ADD with concentration limit ---
            seq3 = [
                ("HOLD", 10, 0.5, 0.3, f"k_h3_{cand['candidate_id']}", True), # 0.5 weight > 0.3 limit
                ("BUY", 10, 0.5, 0.3, f"k_b1_{cand['candidate_id']}", True),
                ("BUY", 10, 0.5, 0.3, f"k_b2_{cand['candidate_id']}", True),
                ("BUY", 10, 0.5, 0.3, f"k_b3_{cand['candidate_id']}", True),
            ]
            r3 = await simulate_sequence(db, p_id, i_id, seq3, overrides)
            
            # Since weight > max_concentration_limit, action should be REDUCE, and ADD count should be 0
            assert r3[-1]["add_count"] == 0
            assert r3[-1]["action"] == LifecycleAction.CONSIDER_REDUCE
            
            await simulate_sequence(db, p_id, i_id, [("HOLD", 0, 0, 0, f"close3_{cand['candidate_id']}", True)], overrides)
            
            # --- Test 4: Missing Valuation (NO_ACTION_DATA) ---
            seq4 = [
                ("HOLD", 10, 0.1, 0.3, f"k_h4_{cand['candidate_id']}", True),
                ("BUY", 10, 0.1, 0.3, f"k_b1_4_{cand['candidate_id']}", False), # is_evaluable=False
            ]
            r4 = await simulate_sequence(db, p_id, i_id, seq4, overrides)
            assert r4[-1]["action"] == LifecycleAction.NO_ACTION_DATA
            
            await simulate_sequence(db, p_id, i_id, [("HOLD", 0, 0, 0, f"close4_{cand['candidate_id']}", True)], overrides)

            # --- Test 5: Single negative then recovery ---
            seq5 = [
                ("HOLD", 10, 0.1, 0.3, f"k_h5_{cand['candidate_id']}", True),
                ("SELL", 10, 0.1, 0.3, f"k_s1_5_{cand['candidate_id']}", True), # WATCH
                ("BUY", 10, 0.1, 0.3, f"k_b1_5_{cand['candidate_id']}", True), # Back to STABLE
            ]
            r5 = await simulate_sequence(db, p_id, i_id, seq5, overrides)
            assert r5[-1]["health"] == LifecycleHealthState.STABLE
            await simulate_sequence(db, p_id, i_id, [("HOLD", 0, 0, 0, f"close5_{cand['candidate_id']}", True)], overrides)

            # --- Test 6: Whipsaw and Recovery sequence ---
            seq6 = [
                ("HOLD", 10, 0.1, 0.3, f"k_h6_{cand['candidate_id']}", True),
                ("SELL", 10, 0.1, 0.3, f"k_w1_{cand['candidate_id']}", True),
                ("SELL", 10, 0.1, 0.3, f"k_w2_{cand['candidate_id']}", True),
                ("SELL", 10, 0.1, 0.3, f"k_w3_{cand['candidate_id']}", True), # CONFIRMED_DETERIORATION
                ("BUY", 10, 0.1, 0.3, f"k_w4_{cand['candidate_id']}", True),  # RECOVERING
                ("SELL", 10, 0.1, 0.3, f"k_w5_{cand['candidate_id']}", True), # Relapse to CONFIRMED_DETERIORATION
                ("BUY", 10, 0.1, 0.3, f"k_w6_{cand['candidate_id']}", True),  # RECOVERING
                ("BUY", 10, 0.1, 0.3, f"k_w7_{cand['candidate_id']}", True),  # STABLE? (Needs RECOVERY_THRESHOLD)
            ]
            r6 = await simulate_sequence(db, p_id, i_id, seq6, overrides)
            rec_thresh = overrides["RECOVERY_THRESHOLD"]
            if rec_thresh <= 2:
                assert r6[-1]["health"] == LifecycleHealthState.STABLE
                
            await simulate_sequence(db, p_id, i_id, [("HOLD", 0, 0, 0, f"close6_{cand['candidate_id']}", True)], overrides)

            # --- Test 7: Context-only portfolio changes & same market obs ---
            seq7 = [
                ("HOLD", 10, 0.1, 0.3, f"k_same", True),
                ("HOLD", 12, 0.12, 0.3, f"k_same", True), # Quantity changes, market key same
            ]
            r7 = await simulate_sequence(db, p_id, i_id, seq7, overrides)
            assert r7[-1]["health"] == r7[-2]["health"]

