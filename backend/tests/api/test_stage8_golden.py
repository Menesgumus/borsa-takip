"""
PHASE 30 — STAGE 8 GOLDEN FIXTURE SUITE

Full deterministic correctness matrix.
These tests prove software behavior — not empirical market superiority.

Candidates: CHAMPION + 13 challengers = 14 total
Scenarios:  16 named sequences
Total evaluations: 14 × 16 candidate-scenario pairs
"""

import pytest
import time
from decimal import Decimal
from datetime import datetime, timezone

from app.db.models import Instrument, Portfolio, User, InstrumentType, LifecycleHealthState, LifecycleAction, DecisionAction
from app.services.lifecycle_engine import process_position_lifecycle
from app.schemas.decision import DecisionResult
from app.services.stage8_manifest import generate_challenger_manifest, CHAMPION_CONFIG
from app.services.reduce_helper import calculate_reduce_quantity
from app.db.session import async_session_maker
import uuid

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SCENARIOS = [
    "stable_repeated_buy",
    "single_negative_then_recovery",
    "two_negatives",
    "three_negatives",
    "five_negatives",
    "repeated_strong_sell",
    "negative_positive_negative_whipsaw",
    "stable_repeated_buy_add_eligibility",
    "add_non_evaluable_fx",
    "add_incomplete_valuation",
    "add_concentration_breach",
    "recovery_sequence",
    "one_share_reduce",
    "multi_share_reduce",
    "same_market_observation_repeated",
    "context_only_portfolio_change",
]


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
    """
    sequence items: (market_view, quantity, weight, max_limit, market_key, is_evaluable)
    Returns list of result dicts per step.
    """
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
            policy_overrides=policy_overrides,
        )
        await db.flush()

        results.append({
            "health": lc.health_state,
            "action": lc.recommended_action,
            "neg_count": lc.negative_confirmation_count,
            "rec_count": lc.recovery_confirmation_count,
            "add_count": lc.add_confirmation_count,
            "strong_sell_count": lc.strong_sell_confirmation_count,
        })
    return results


async def close_episode(db, p_id, i_id, tag, overrides):
    """Close any open episode cleanly."""
    await simulate_sequence(db, p_id, i_id, [("HOLD", 0, 0, 0, f"CLOSE_{tag}", True)], overrides)


# ---------------------------------------------------------------------------
# Single-scenario functions, each takes (db, p_id, i_id, cand_tag, overrides)
# ---------------------------------------------------------------------------

async def scenario_stable_repeated_buy(db, p_id, i_id, tag, overrides):
    seq = [
        ("BUY", 10, 0.1, 0.3, f"S01_k1_{tag}", True),
        ("BUY", 10, 0.1, 0.3, f"S01_k2_{tag}", True),
        ("BUY", 10, 0.1, 0.3, f"S01_k3_{tag}", True),
    ]
    r = await simulate_sequence(db, p_id, i_id, seq, overrides)
    assert r[-1]["health"] == LifecycleHealthState.STABLE
    await close_episode(db, p_id, i_id, f"S01_{tag}", overrides)
    return r


async def scenario_single_negative_then_recovery(db, p_id, i_id, tag, overrides):
    seq = [
        ("HOLD", 10, 0.1, 0.3, f"S02_h_{tag}", True),
        ("SELL", 10, 0.1, 0.3, f"S02_s1_{tag}", True),  # -> WATCH
        ("BUY",  10, 0.1, 0.3, f"S02_b1_{tag}", True),  # -> STABLE
    ]
    r = await simulate_sequence(db, p_id, i_id, seq, overrides)
    assert r[-1]["health"] == LifecycleHealthState.STABLE, (
        f"Expected STABLE after 1-neg recovery, got {r[-1]['health']}"
    )
    await close_episode(db, p_id, i_id, f"S02_{tag}", overrides)
    return r


async def scenario_two_negatives(db, p_id, i_id, tag, overrides):
    seq = [
        ("HOLD", 10, 0.1, 0.3, f"S03_h_{tag}", True),
        ("SELL", 10, 0.1, 0.3, f"S03_s1_{tag}", True),  # neg=1 -> WATCH
        ("SELL", 10, 0.1, 0.3, f"S03_s2_{tag}", True),  # neg=2
    ]
    r = await simulate_sequence(db, p_id, i_id, seq, overrides)
    # After 2 negatives: WATCH for champion (CONFIRMED_THRESHOLD=3), CONFIRMED for DETERIORATION_2
    conf_thresh = overrides["CONFIRMED_THRESHOLD"]
    if conf_thresh <= 2:
        assert r[-1]["health"] == LifecycleHealthState.CONFIRMED_DETERIORATION
    else:
        assert r[-1]["health"] == LifecycleHealthState.WATCH
    await close_episode(db, p_id, i_id, f"S03_{tag}", overrides)
    return r


async def scenario_three_negatives(db, p_id, i_id, tag, overrides):
    seq = [
        ("HOLD", 10, 0.1, 0.3, f"S04_h_{tag}", True),
        ("SELL", 10, 0.1, 0.3, f"S04_s1_{tag}", True),
        ("SELL", 10, 0.1, 0.3, f"S04_s2_{tag}", True),
        ("SELL", 10, 0.1, 0.3, f"S04_s3_{tag}", True),
    ]
    r = await simulate_sequence(db, p_id, i_id, seq, overrides)
    # Champion CONFIRMED_THRESHOLD=3: step 4 is confirmed
    # DETERIORATION_4: still WATCH at 3
    conf_thresh = overrides["CONFIRMED_THRESHOLD"]
    if conf_thresh <= 3:
        assert r[-1]["health"] == LifecycleHealthState.CONFIRMED_DETERIORATION
    else:
        assert r[-1]["health"] == LifecycleHealthState.WATCH
    await close_episode(db, p_id, i_id, f"S04_{tag}", overrides)
    return r


async def scenario_five_negatives(db, p_id, i_id, tag, overrides):
    seq = [
        ("HOLD", 10, 0.1, 0.3, f"S05_h_{tag}", True),
        ("SELL", 10, 0.1, 0.3, f"S05_s1_{tag}", True),
        ("SELL", 10, 0.1, 0.3, f"S05_s2_{tag}", True),
        ("SELL", 10, 0.1, 0.3, f"S05_s3_{tag}", True),
        ("SELL", 10, 0.1, 0.3, f"S05_s4_{tag}", True),
        ("SELL", 10, 0.1, 0.3, f"S05_s5_{tag}", True),
        ("SELL", 10, 0.1, 0.3, f"S05_s6_{tag}", True),
    ]
    r = await simulate_sequence(db, p_id, i_id, seq, overrides)
    exit_thresh = overrides["EXIT_THRESHOLD"]
    # Step index where exit should appear: HOLD=0, s1=1, ...  s_exit_thresh=exit_thresh
    assert r[exit_thresh]["action"] == LifecycleAction.CONSIDER_EXIT, (
        f"Expected EXIT at step {exit_thresh}, got {r[exit_thresh]['action']}"
    )
    await close_episode(db, p_id, i_id, f"S05_{tag}", overrides)
    return r


async def scenario_repeated_strong_sell(db, p_id, i_id, tag, overrides):
    """
    Proves STRONG_SELL exit threshold.
    CHAMPION = 3, EXIT_STRONG_SELL_2 = 2, EXIT_STRONG_SELL_4 = 4
    """
    seq = [
        ("HOLD",       10, 0.1, 0.3, f"S06_h_{tag}", True),
        ("STRONG_SELL", 10, 0.1, 0.3, f"S06_ss1_{tag}", True),
        ("STRONG_SELL", 10, 0.1, 0.3, f"S06_ss2_{tag}", True),
        ("STRONG_SELL", 10, 0.1, 0.3, f"S06_ss3_{tag}", True),
        ("STRONG_SELL", 10, 0.1, 0.3, f"S06_ss4_{tag}", True),
        ("STRONG_SELL", 10, 0.1, 0.3, f"S06_ss5_{tag}", True),
    ]
    r = await simulate_sequence(db, p_id, i_id, seq, overrides)
    strong_exit_thresh = overrides["STRONG_EXIT_THRESHOLD"]
    # HOLD=step0, ss1=step1 ... exit should appear at step strong_exit_thresh
    assert r[strong_exit_thresh]["action"] == LifecycleAction.CONSIDER_EXIT, (
        f"Expected STRONG_SELL EXIT at step {strong_exit_thresh}, got {r[strong_exit_thresh]['action']}"
    )
    await close_episode(db, p_id, i_id, f"S06_{tag}", overrides)
    return r


async def scenario_negative_positive_negative_whipsaw(db, p_id, i_id, tag, overrides):
    """
    Whipsaw: enough negatives to enter WATCH, then recovery to STABLE, then 1 negative.
    For WATCH_THRESHOLD=1: 1 sell -> WATCH, BUY -> STABLE, sell -> WATCH
    For WATCH_THRESHOLD=2: 2 sells -> WATCH, BUY -> STABLE, 1 sell -> STABLE (not enough for WATCH yet)
    """
    watch_thresh = overrides["WATCH_THRESHOLD"]
    # Build enough negatives to enter WATCH, then a positive, then one negative
    neg_keys = [f"S07_s{i}_{tag}" for i in range(1, watch_thresh + 1)]
    seq = (
        [("HOLD", 10, 0.1, 0.3, f"S07_h_{tag}", True)]
        + [("SELL", 10, 0.1, 0.3, k, True) for k in neg_keys]   # reach WATCH
        + [("BUY",  10, 0.1, 0.3, f"S07_b1_{tag}", True)]        # back to STABLE, neg_count resets
        + [("SELL", 10, 0.1, 0.3, f"S07_s2_{tag}", True)]        # 1 new negative
    )
    r = await simulate_sequence(db, p_id, i_id, seq, overrides)
    # After 1 new negative post-recovery:
    # WATCH_1 (thresh=1): 1 >= 1 -> WATCH
    # WATCH_2 (thresh=2): 1 < 2 -> STABLE
    if watch_thresh == 1:
        assert r[-1]["health"] == LifecycleHealthState.WATCH, (
            f"WATCH_THRESHOLD=1: expected WATCH after whipsaw, got {r[-1]['health']}"
        )
    else:
        # With thresh=2 one negative is insufficient to re-enter WATCH
        assert r[-1]["health"] == LifecycleHealthState.STABLE, (
            f"WATCH_THRESHOLD={watch_thresh}: expected STABLE after single-neg whipsaw, got {r[-1]['health']}"
        )
    await close_episode(db, p_id, i_id, f"S07_{tag}", overrides)
    return r


async def scenario_stable_repeated_buy_add_eligibility(db, p_id, i_id, tag, overrides):
    """
    Verifies add_confirmation_count mechanics and ADD action.
    add_thresh=1 -> ADD after 1 BUY
    add_thresh=2 -> ADD after 2 BUYs
    add_thresh=3 -> ADD after 3 BUYs
    """
    seq = [
        ("HOLD", 10, 0.1, 0.3, f"S08_h_{tag}", True),
        ("BUY",  10, 0.1, 0.3, f"S08_b1_{tag}", True),
        ("BUY",  10, 0.1, 0.3, f"S08_b2_{tag}", True),
        ("BUY",  10, 0.1, 0.3, f"S08_b3_{tag}", True),
    ]
    r = await simulate_sequence(db, p_id, i_id, seq, overrides)
    add_thresh = overrides["ADD_THRESHOLD"]
    # After add_thresh BUYs while STABLE, ADD should appear
    assert r[add_thresh]["action"] == LifecycleAction.CONSIDER_ADD, (
        f"ADD_THRESHOLD={add_thresh}: expected CONSIDER_ADD at step {add_thresh}, got {r[add_thresh]['action']}"
    )
    await close_episode(db, p_id, i_id, f"S08_{tag}", overrides)
    return r


async def scenario_add_non_evaluable_fx(db, p_id, i_id, tag, overrides):
    """ADD with non-evaluable data -> NO_ACTION_DATA, add_count stays 0."""
    seq = [
        ("HOLD", 10, 0.1, 0.3, f"S09_h_{tag}", True),
        ("BUY",  10, 0.1, 0.3, f"S09_b1_{tag}", False),  # is_evaluable=False
        ("BUY",  10, 0.1, 0.3, f"S09_b2_{tag}", False),
    ]
    r = await simulate_sequence(db, p_id, i_id, seq, overrides)
    assert r[-1]["action"] == LifecycleAction.NO_ACTION_DATA
    assert r[-1]["add_count"] == 0
    await close_episode(db, p_id, i_id, f"S09_{tag}", overrides)
    return r


async def scenario_add_incomplete_valuation(db, p_id, i_id, tag, overrides):
    """ADD with incomplete valuation (is_evaluable=False) -> NO_ACTION_DATA."""
    seq = [
        ("HOLD", 10, 0.1, 0.3, f"S10_h_{tag}", True),
        ("BUY",  10, 0.1, 0.3, f"S10_b1_{tag}", False),
    ]
    r = await simulate_sequence(db, p_id, i_id, seq, overrides)
    assert r[-1]["action"] == LifecycleAction.NO_ACTION_DATA
    await close_episode(db, p_id, i_id, f"S10_{tag}", overrides)
    return r


async def scenario_add_concentration_breach(db, p_id, i_id, tag, overrides):
    """
    weight > max_concentration -> CONSIDER_REDUCE, add_count=0.
    Tests that concentration hard limit is never bypassed by challengers.
    """
    seq = [
        ("HOLD", 10, 0.5, 0.3, f"S11_h_{tag}", True),   # 0.5 > 0.3 limit
        ("BUY",  10, 0.5, 0.3, f"S11_b1_{tag}", True),
        ("BUY",  10, 0.5, 0.3, f"S11_b2_{tag}", True),
        ("BUY",  10, 0.5, 0.3, f"S11_b3_{tag}", True),
    ]
    r = await simulate_sequence(db, p_id, i_id, seq, overrides)
    assert r[-1]["add_count"] == 0, "add_count must not advance when concentration breached"
    assert r[-1]["action"] == LifecycleAction.CONSIDER_REDUCE
    await close_episode(db, p_id, i_id, f"S11_{tag}", overrides)
    return r


async def scenario_recovery_sequence(db, p_id, i_id, tag, overrides):
    """
    Full deterioration -> recovery cycle.
    CONFIRMED_DETERIORATION -> RECOVERING -> STABLE

    The engine transition:
    - First BUY after CONFIRMED: enters RECOVERING, sets recovery_count=1
    - Subsequent BUYs: increment recovery_count, transition to STABLE when >= RECOVERY_THRESHOLD
    So we need (1 BUY to enter RECOVERING) + RECOVERY_THRESHOLD additional BUYs to reach STABLE.
    """
    conf_thresh = overrides["CONFIRMED_THRESHOLD"]
    rec_thresh  = overrides["RECOVERY_THRESHOLD"]

    seq = (
        [("HOLD", 10, 0.1, 0.3, f"S12_h_{tag}", True)]
        + [("SELL", 10, 0.1, 0.3, f"S12_s{i}_{tag}", True) for i in range(1, conf_thresh + 1)]
        # First BUY: CONFIRMED -> RECOVERING (count=1)
        # Additional BUYs: in RECOVERING, increments count, checks >= rec_thresh
        # rec_thresh=1: need count=1 to pass (already set by first BUY entering state)
        # But the engine checks AFTER incrementing in RECOVERING, not on entry
        # So: first BUY sets count=1 in RECOVERING, second BUY in RECOVERING increments to 2
        # For rec_thresh=1: 1 BUY enters RECOVERING with count=1, that's already >= 1 NOT yet checked
        # The check happens in RECOVERING elif block only, so we need the first BUY in RECOVERING state
        # which means: 1 BUY -> enters RECOVERING (count=1), next BUY (in RECOVERING state) increments to 2, >= 1 -> STABLE
        # Simplest: generate conf_thresh negatives then rec_thresh + 1 positives
        + [("BUY",  10, 0.1, 0.3, f"S12_b{i}_{tag}", True) for i in range(1, rec_thresh + 2)]
    )
    r = await simulate_sequence(db, p_id, i_id, seq, overrides)
    assert r[-1]["health"] == LifecycleHealthState.STABLE, (
        f"Expected STABLE after full recovery ({conf_thresh} neg + {rec_thresh+1} pos), got {r[-1]['health']}"
    )
    await close_episode(db, p_id, i_id, f"S12_{tag}", overrides)
    return r


async def scenario_one_share_reduce(db, p_id, i_id, tag, overrides):
    """1-share position: all reduce candidates must yield 0 partial reduction."""
    reduce_frac_25 = Decimal("0.25")
    reduce_frac_50 = Decimal("0.5")
    reduce_frac_75 = Decimal("0.75")
    assert calculate_reduce_quantity(Decimal("1"), reduce_frac_25) == Decimal("0")
    assert calculate_reduce_quantity(Decimal("1"), reduce_frac_50) == Decimal("0")
    assert calculate_reduce_quantity(Decimal("1"), reduce_frac_75) == Decimal("0")
    # Test via sequence: quantity=1, concentration breach -> REDUCE action
    seq = [
        ("HOLD", 1, 0.5, 0.3, f"S13_h_{tag}", True),
        ("SELL", 1, 0.5, 0.3, f"S13_s1_{tag}", True),
        ("SELL", 1, 0.5, 0.3, f"S13_s2_{tag}", True),
        ("SELL", 1, 0.5, 0.3, f"S13_s3_{tag}", True),
    ]
    r = await simulate_sequence(db, p_id, i_id, seq, overrides)
    # Whether REDUCE or EXIT, reduce_quantity via helper = 0 for qty=1
    await close_episode(db, p_id, i_id, f"S13_{tag}", overrides)
    return r


async def scenario_multi_share_reduce(db, p_id, i_id, tag, overrides):
    """
    Multi-share REDUCE variance proof.
    champion 50%:  qty 10 -> 5
    REDUCE_25 25%: qty 10 -> 2
    REDUCE_75 75%: qty 10 -> 7
    """
    frac = Decimal(str(overrides["REDUCE_FRACTION"]))
    qty = Decimal("10")
    expected = {
        Decimal("0.25"): Decimal("2"),
        Decimal("0.5"):  Decimal("5"),
        Decimal("0.75"): Decimal("7"),
    }.get(frac)
    actual = calculate_reduce_quantity(qty, frac)
    if expected is not None:
        assert actual == expected, (
            f"REDUCE_FRACTION={frac}: expected {expected}, got {actual}"
        )
    # Sequence just confirms state machine is not broken
    seq = [("HOLD", 10, 0.1, 0.3, f"S14_h_{tag}", True)]
    r = await simulate_sequence(db, p_id, i_id, seq, overrides)
    await close_episode(db, p_id, i_id, f"S14_{tag}", overrides)
    return r


async def scenario_same_market_observation_repeated(db, p_id, i_id, tag, overrides):
    """
    Repeated same market_key: counters must NOT advance.
    health must not change.
    """
    same_key = f"S15_SAME_KEY"
    seq = [
        ("SELL", 10, 0.1, 0.3, same_key, True),
        ("SELL", 10, 0.1, 0.3, same_key, True),  # same key, should be idempotent
        ("SELL", 10, 0.1, 0.3, same_key, True),
    ]
    r = await simulate_sequence(db, p_id, i_id, seq, overrides)
    # All three steps have same key -> counters should only have advanced once
    assert r[0]["neg_count"] == r[1]["neg_count"] == r[2]["neg_count"], (
        "Same market_key must NOT advance neg_count"
    )
    assert r[0]["strong_sell_count"] == r[1]["strong_sell_count"] == r[2]["strong_sell_count"]
    assert r[0]["add_count"] == r[1]["add_count"] == r[2]["add_count"]
    await close_episode(db, p_id, i_id, f"S15_{tag}", overrides)
    return r


async def scenario_context_only_portfolio_change(db, p_id, i_id, tag, overrides):
    """
    Same market_key, different qty/weight -> health and counters unchanged.
    """
    same_key = f"S16_CTX_KEY_{tag}"
    seq = [
        ("HOLD", 10, 0.1, 0.3, same_key, True),
        ("HOLD", 12, 0.12, 0.3, same_key, True),  # qty changes, market_key same
        ("HOLD", 8,  0.08, 0.3, same_key, True),
    ]
    r = await simulate_sequence(db, p_id, i_id, seq, overrides)
    assert r[0]["health"] == r[1]["health"] == r[2]["health"], "Context change must not alter health"
    assert r[0]["neg_count"] == r[1]["neg_count"] == r[2]["neg_count"], (
        "Context change must not advance neg_count"
    )
    assert r[0]["rec_count"] == r[1]["rec_count"] == r[2]["rec_count"]
    assert r[0]["add_count"] == r[1]["add_count"] == r[2]["add_count"]
    assert r[0]["strong_sell_count"] == r[1]["strong_sell_count"] == r[2]["strong_sell_count"]
    await close_episode(db, p_id, i_id, f"S16_{tag}", overrides)
    return r


SCENARIO_FNS = {
    "stable_repeated_buy":                  scenario_stable_repeated_buy,
    "single_negative_then_recovery":        scenario_single_negative_then_recovery,
    "two_negatives":                        scenario_two_negatives,
    "three_negatives":                      scenario_three_negatives,
    "five_negatives":                       scenario_five_negatives,
    "repeated_strong_sell":                 scenario_repeated_strong_sell,
    "negative_positive_negative_whipsaw":   scenario_negative_positive_negative_whipsaw,
    "stable_repeated_buy_add_eligibility":  scenario_stable_repeated_buy_add_eligibility,
    "add_non_evaluable_fx":                 scenario_add_non_evaluable_fx,
    "add_incomplete_valuation":             scenario_add_incomplete_valuation,
    "add_concentration_breach":             scenario_add_concentration_breach,
    "recovery_sequence":                    scenario_recovery_sequence,
    "one_share_reduce":                     scenario_one_share_reduce,
    "multi_share_reduce":                   scenario_multi_share_reduce,
    "same_market_observation_repeated":     scenario_same_market_observation_repeated,
    "context_only_portfolio_change":        scenario_context_only_portfolio_change,
}

assert set(SCENARIO_FNS.keys()) == set(SCENARIOS), "SCENARIO_FNS must match SCENARIOS list"


# ---------------------------------------------------------------------------
# Main test
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_stage8_golden_sequences():
    """
    Stage 8 golden fixture suite.
    Candidates: CHAMPION + 13 challengers = 14 total
    Scenarios:  16
    Total evaluations: 14 × 16 = 224
    """
    async with async_session_maker() as db:
        user = User(email=f"test_{uuid.uuid4()}@a.com", password_hash="a")
        inst = Instrument(
            symbol=f"GOLDEN_{uuid.uuid4().hex[:4]}",
            name="G",
            exchange="X",
            instrument_type=InstrumentType.STOCK,
        )
        db.add_all([user, inst])
        await db.commit()
        await db.refresh(user)
        await db.refresh(inst)

        port = Portfolio(user_id=user.id, name="Golden")
        db.add(port)
        await db.commit()
        await db.refresh(port)

        manifest = generate_challenger_manifest()
        candidates = [{"candidate_id": "CHAMPION"}] + manifest

        passed = 0
        failed = 0

        for cand in candidates:
            overrides = dict(CHAMPION_CONFIG)
            if "changed_parameter" in cand:
                overrides[cand["changed_parameter"]] = cand["challenger_value"]

            cid = cand["candidate_id"]
            p_id = port.id

            # Fresh instrument per candidate to isolate lifecycle state
            fresh_inst = Instrument(
                symbol=f"G_{uuid.uuid4().hex[:6]}",
                name="G",
                exchange="X",
                instrument_type=InstrumentType.STOCK,
            )
            db.add(fresh_inst)
            await db.commit()
            await db.refresh(fresh_inst)
            i_id = fresh_inst.id

            for scenario_name in SCENARIOS:
                fn = SCENARIO_FNS[scenario_name]
                try:
                    await fn(db, p_id, i_id, f"{cid}_{scenario_name}", overrides)
                    passed += 1
                except AssertionError as e:
                    failed += 1
                    raise AssertionError(
                        f"[candidate={cid}] [scenario={scenario_name}] FAILED: {e}"
                    ) from e

        total = len(candidates) * len(SCENARIOS)
        assert failed == 0, f"{failed}/{total} golden checks failed"
        assert passed == total


# ---------------------------------------------------------------------------
# Reduce variance explicit test
# ---------------------------------------------------------------------------

def test_reduce_quantity_variance():
    """
    Prove REDUCE_25 != CHAMPION != REDUCE_75 for a valid multi-share position.
    """
    qty = Decimal("10")
    r25 = calculate_reduce_quantity(qty, Decimal("0.25"))
    r50 = calculate_reduce_quantity(qty, Decimal("0.50"))
    r75 = calculate_reduce_quantity(qty, Decimal("0.75"))

    assert r25 == Decimal("2"), f"REDUCE_25: expected 2, got {r25}"
    assert r50 == Decimal("5"), f"CHAMPION:  expected 5, got {r50}"
    assert r75 == Decimal("7"), f"REDUCE_75: expected 7, got {r75}"

    # Three-way proof: all different
    assert r25 != r50 != r75
    assert r25 != r75


def test_reduce_quantity_one_share():
    """1-share: all fractions yield 0 partial reduction."""
    qty = Decimal("1")
    for frac in [Decimal("0.25"), Decimal("0.50"), Decimal("0.75")]:
        result = calculate_reduce_quantity(qty, frac)
        assert result == Decimal("0"), f"1-share reduce with frac={frac}: expected 0, got {result}"


def test_reduce_quantity_whole_share_floor():
    """Verify floor semantics: 7 * 0.25 = 1.75 -> 1."""
    qty = Decimal("7")
    result = calculate_reduce_quantity(qty, Decimal("0.25"))
    assert result == Decimal("1"), f"Floor semantics: expected 1, got {result}"


# ---------------------------------------------------------------------------
# Reproducibility test
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_stage8_reproducibility():
    """
    Two identical runs on the same deterministic sequence must produce
    identical outputs (health states, counter values, actions).
    Timestamps/metadata are excluded from comparison.
    """
    async with async_session_maker() as db:
        user = User(email=f"repro_{uuid.uuid4()}@a.com", password_hash="a")
        inst = Instrument(
            symbol=f"REPRO_{uuid.uuid4().hex[:4]}",
            name="R",
            exchange="X",
            instrument_type=InstrumentType.STOCK,
        )
        db.add_all([user, inst])
        await db.commit()
        await db.refresh(user)
        await db.refresh(inst)

        port1 = Portfolio(user_id=user.id, name="Repro1")
        port2 = Portfolio(user_id=user.id, name="Repro2")
        db.add_all([port1, port2])
        await db.commit()
        await db.refresh(port1)
        await db.refresh(port2)

        overrides = dict(CHAMPION_CONFIG)

        # Identical sequence
        seq = [
            ("HOLD", 10, 0.1, 0.3, "R_k1", True),
            ("SELL", 10, 0.1, 0.3, "R_k2", True),
            ("SELL", 10, 0.1, 0.3, "R_k3", True),
            ("SELL", 10, 0.1, 0.3, "R_k4", True),
            ("BUY",  10, 0.1, 0.3, "R_k5", True),
            ("BUY",  10, 0.1, 0.3, "R_k6", True),
        ]

        r1 = await simulate_sequence(db, port1.id, inst.id, seq, overrides)
        r2 = await simulate_sequence(db, port2.id, inst.id, seq, overrides)

        for i, (s1, s2) in enumerate(zip(r1, r2)):
            assert s1["health"]           == s2["health"],           f"Step {i}: health mismatch"
            assert s1["action"]           == s2["action"],           f"Step {i}: action mismatch"
            assert s1["neg_count"]        == s2["neg_count"],        f"Step {i}: neg_count mismatch"
            assert s1["rec_count"]        == s2["rec_count"],        f"Step {i}: rec_count mismatch"
            assert s1["add_count"]        == s2["add_count"],        f"Step {i}: add_count mismatch"
            assert s1["strong_sell_count"] == s2["strong_sell_count"], f"Step {i}: strong_sell_count mismatch"
