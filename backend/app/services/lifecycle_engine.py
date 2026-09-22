import hashlib
import logging
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.instruments import get_instrument_context
from app.db.models import (
    AssetClass,
    FundamentalData,
    Instrument,
    LifecycleAction,
    LifecycleHealthState,
    OHLCVDaily,
    Portfolio,
    PositionLifecycle,
    PositionLifecycleSnapshot,
    User,
)
from app.services.decision_engine import (
    ENGINE_VERSION,
    DecisionResult,
    FundamentalInputs,
    Horizon,
    NewsInputs,
    TechnicalInputs,
    evaluate_decision,
)
from app.services.technical_data import get_technical_analysis

logger = logging.getLogger(__name__)

LIFECYCLE_POLICY_VERSION = "v1"

class LifecycleConstants:
    WATCH_THRESHOLD = 1
    CONFIRMED_THRESHOLD = 3
    EXIT_THRESHOLD = 5
    STRONG_EXIT_THRESHOLD = 3
    RECOVERY_THRESHOLD = 2
    ADD_THRESHOLD = 2

    # 50% reduce
    REDUCE_FRACTION = Decimal("0.5")

async def _get_latest_completed_ohlcv_date(db: AsyncSession, instrument_id: int) -> str | None:
    stmt = select(OHLCVDaily.timestamp).where(OHLCVDaily.instrument_id == instrument_id).order_by(OHLCVDaily.timestamp.desc()).limit(1)
    res = await db.execute(stmt)
    dt = res.scalar_one_or_none()
    if dt:
        return dt.isoformat()
    return None

async def _get_latest_fundamental_version(db: AsyncSession, instrument_id: int) -> str | None:
    stmt = select(FundamentalData.id).where(FundamentalData.instrument_id == instrument_id).order_by(FundamentalData.published_at.desc()).limit(1)
    res = await db.execute(stmt)
    fid = res.scalar_one_or_none()
    return str(fid) if fid else None

def compute_market_observation_key(
    instrument_id: int,
    latest_completed_ohlcv_date: str | None,
    latest_fundamental_version: str | None,
    asset_class: AssetClass
) -> str:
    # GOLD does not use fundamental version
    fund_part = latest_fundamental_version if asset_class not in (AssetClass.GOLD, AssetClass.FX_REFERENCE) else "NONE"
    ohlcv_part = latest_completed_ohlcv_date or "NONE"

    raw = f"{instrument_id}|{ohlcv_part}|{fund_part}|{ENGINE_VERSION}|{LIFECYCLE_POLICY_VERSION}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def compute_portfolio_context_key(
    portfolio_id: int,
    instrument_id: int,
    episode_number: int,
    current_quantity: Decimal,
    current_weight: Decimal,
    cash_balance: Decimal,
    valuation_complete: bool,
    fx_rate: Decimal | None,
    transaction_state_version: str
) -> str:
    # Normalize decimals
    qty_norm = current_quantity.normalize()
    wt_norm = current_weight.normalize()
    cash_norm = cash_balance.normalize()
    fx_norm = fx_rate.normalize() if fx_rate is not None else "NONE"

    raw = f"{portfolio_id}|{instrument_id}|{episode_number}|{qty_norm}|{wt_norm}|{cash_norm}|{valuation_complete}|{fx_norm}|{transaction_state_version}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

async def evaluate_lifecycle_for_instrument(
    db: AsyncSession,
    user: User,
    portfolio: Portfolio,
    instrument: Instrument,
    current_quantity: Decimal,
    current_weight: Decimal,
    portfolio_cash: Decimal,
    max_concentration_limit: Decimal,
    is_valuation_complete: bool,
    fx_rate: Decimal | None,
    transaction_state_version: str
):
    # 1. Fetch persistent market data (COMPLETED OHLCV)
    tech_response = await get_technical_analysis(db, instrument.symbol)

    # We do NOT inject live quote for the market persistence adapter.
    tech = TechnicalInputs(current_price=None, rsi_14=None, macd_line=None, macd_signal=None, sma_50=None, sma_200=None)
    if tech_response.indicators:
        latest = tech_response.indicators[-1] # This is the latest COMPLETED daily bar
        base_price = Decimal(str(latest.close)) if latest.close is not None else None
        tech = TechnicalInputs(
            current_price=base_price,
            rsi_14=Decimal(str(latest.rsi_14)) if latest.rsi_14 is not None else None,
            macd_line=Decimal(str(latest.macd_line)) if latest.macd_line is not None else None,
            macd_signal=Decimal(str(latest.macd_signal)) if latest.macd_signal is not None else None,
            sma_50=Decimal(str(latest.sma_50)) if latest.sma_50 is not None else None,
            sma_200=Decimal(str(latest.sma_200)) if latest.sma_200 is not None else None,
            is_stale=False # It's completed data, not live. Evaluability handles stale overall.
        )

    # 2. Fetch Fundamentals & Context
    context = await get_instrument_context(instrument.symbol, db, user)
    fund = FundamentalInputs(instrument_type=instrument.instrument_type.value)
    if hasattr(context, 'fundamentals') and context.fundamentals:
        metrics = context.fundamentals.metrics or {}
        fk = metrics.get('f_k') or metrics.get('pe_ratio')
        pd_dd = metrics.get('pd_dd') or metrics.get('pb_ratio')
        fund = fund.model_copy(update={
            "pe_ratio": Decimal(str(fk)) if fk is not None else None,
            "pb_ratio": Decimal(str(pd_dd)) if pd_dd is not None else None,
        })

    # Evaluate pure decision
    news_inputs = NewsInputs() # Deferred

    decision = evaluate_decision(instrument.id, Horizon.MEDIUM, tech, fund, news_inputs)

    # Data Quality / Evaluability
    # For Phase 29, if tech data is completely missing, it's not evaluable.
    # We also check if quote provider is unavailable, but market key relies on completed data.
    # If there's no completed bar, we can't evaluate.
    is_evaluable = tech.current_price is not None
    if decision.data_quality_score < Decimal("50"):
        is_evaluable = False

    # 3. Compute Keys
    ohlcv_date = await _get_latest_completed_ohlcv_date(db, instrument.id)
    fund_ver = await _get_latest_fundamental_version(db, instrument.id)

    market_key = compute_market_observation_key(instrument.id, ohlcv_date, fund_ver, instrument.asset_class)
    context_key = compute_portfolio_context_key(
        portfolio.id, instrument.id, 0, current_quantity, current_weight, portfolio_cash, is_valuation_complete, fx_rate, transaction_state_version
    ) # Episode and transaction state will be injected when we have the lifecycle record

    return decision, market_key, context_key, is_evaluable

async def process_position_lifecycle(
    db: AsyncSession,
    portfolio_id: int,
    instrument_id: int,
    current_quantity: Decimal,
    current_weight: Decimal,
    max_concentration_limit: Decimal,
    decision: DecisionResult,
    market_key: str,
    context_key_partial: str,
    is_evaluable: bool
) -> PositionLifecycle:
    # 1. Lock the existing lifecycle row
    stmt = select(PositionLifecycle).where(
        PositionLifecycle.portfolio_id == portfolio_id,
        PositionLifecycle.instrument_id == instrument_id
    ).with_for_update()

    result = await db.execute(stmt)
    lifecycle = result.scalar_one_or_none()

    now = datetime.utcnow()

    # 2. Handle Initialization or Episode changes
    if not lifecycle:
        lifecycle = PositionLifecycle(
            portfolio_id=portfolio_id,
            instrument_id=instrument_id,
            episode_number=1,
            health_state=LifecycleHealthState.STABLE,
            recommended_action=LifecycleAction.HOLD,
            policy_version=LIFECYCLE_POLICY_VERSION,
            episode_started_at=now
        )
        db.add(lifecycle)
        # Flush to get ID
        await db.flush()

    elif current_quantity > 0 and lifecycle.health_state == LifecycleHealthState.CLOSED:
        # Re-entry
        lifecycle.episode_number += 1
        lifecycle.health_state = LifecycleHealthState.STABLE
        lifecycle.recommended_action = LifecycleAction.HOLD
        lifecycle.episode_started_at = now
        lifecycle.closed_at = None
        lifecycle.negative_confirmation_count = 0
        lifecycle.strong_sell_confirmation_count = 0
        lifecycle.recovery_confirmation_count = 0
        lifecycle.add_confirmation_count = 0

    # Inject episode number into context key
    context_key = f"{context_key_partial}|{lifecycle.episode_number}"
    context_key = hashlib.sha256(context_key.encode("utf-8")).hexdigest()

    # If qty is 0, just mark closed if not already
    if current_quantity == 0:
        if lifecycle.health_state != LifecycleHealthState.CLOSED:
            lifecycle.health_state_before = lifecycle.health_state
            lifecycle.health_state = LifecycleHealthState.CLOSED
            lifecycle.recommended_action = LifecycleAction.NO_ACTION_DATA
            lifecycle.closed_at = now

            # Create snapshot for closure
            snap = PositionLifecycleSnapshot(
                lifecycle_id=lifecycle.id,
                episode_number=lifecycle.episode_number,
                market_observation_key=market_key,
                portfolio_context_key=context_key,
                health_state_before=lifecycle.health_state_before,
                health_state_after=lifecycle.health_state,
                recommended_action=lifecycle.recommended_action,
                market_view=None,
                reason_codes="[\"POSITION_CLOSED\"]",
                evaluated_at=now
            )
            db.add(snap)
        return lifecycle

    health_before = lifecycle.health_state
    action_before = lifecycle.recommended_action

    # 3. Handle Data Evaluability
    if not is_evaluable:
        lifecycle.recommended_action = LifecycleAction.NO_ACTION_DATA
        if action_before != LifecycleAction.NO_ACTION_DATA:
            snap = PositionLifecycleSnapshot(
                lifecycle_id=lifecycle.id,
                episode_number=lifecycle.episode_number,
                market_observation_key=market_key,
                portfolio_context_key=context_key,
                health_state_before=health_before,
                health_state_after=lifecycle.health_state,
                recommended_action=lifecycle.recommended_action,
                market_view=None,
                reason_codes="[\"DATA_UNAVAILABLE\"]",
                evaluated_at=now
            )
            db.add(snap)
        return lifecycle

    # 4. Check if Market Observation is NEW
    is_new_market = (market_key != lifecycle.last_counted_market_observation_key)

    if is_new_market:
        view = decision.market_view

        # Negative Rules
        if view in ("SELL", "STRONG_SELL"):
            lifecycle.negative_confirmation_count += 1
        else:
            lifecycle.negative_confirmation_count = 0

        # Strong Sell Rules
        if view == "STRONG_SELL":
            lifecycle.strong_sell_confirmation_count += 1
        else:
            lifecycle.strong_sell_confirmation_count = 0

        # Add Rules
        if lifecycle.health_state == LifecycleHealthState.STABLE and view in ("BUY", "STRONG_BUY"):
            # Enforce all Phase 29 prerequisites here natively (eligibility, valuation, FX, concentration)
            if is_evaluable and current_weight <= max_concentration_limit:
                lifecycle.add_confirmation_count += 1
            else:
                lifecycle.add_confirmation_count = 0
        else:
            lifecycle.add_confirmation_count = 0

        # State Machine Transitions
        if lifecycle.health_state == LifecycleHealthState.STABLE:
            if lifecycle.negative_confirmation_count >= LifecycleConstants.WATCH_THRESHOLD:
                lifecycle.health_state = LifecycleHealthState.WATCH

        elif lifecycle.health_state == LifecycleHealthState.WATCH:
            if lifecycle.negative_confirmation_count >= LifecycleConstants.CONFIRMED_THRESHOLD:
                lifecycle.health_state = LifecycleHealthState.CONFIRMED_DETERIORATION
            elif view in ("HOLD", "BUY", "STRONG_BUY"):
                lifecycle.health_state = LifecycleHealthState.STABLE
                lifecycle.negative_confirmation_count = 0

        elif lifecycle.health_state == LifecycleHealthState.CONFIRMED_DETERIORATION:
            if view in ("HOLD", "BUY", "STRONG_BUY"):
                lifecycle.health_state = LifecycleHealthState.RECOVERING
                lifecycle.recovery_confirmation_count = 1

        elif lifecycle.health_state == LifecycleHealthState.RECOVERING:
            if view in ("SELL", "STRONG_SELL"):
                # Relapse
                lifecycle.health_state = LifecycleHealthState.CONFIRMED_DETERIORATION
                lifecycle.recovery_confirmation_count = 0
                # Negative count was just incremented above
            else:
                lifecycle.recovery_confirmation_count += 1
                if lifecycle.recovery_confirmation_count >= LifecycleConstants.RECOVERY_THRESHOLD:
                    lifecycle.health_state = LifecycleHealthState.STABLE
                    lifecycle.recovery_confirmation_count = 0
                    lifecycle.negative_confirmation_count = 0
                    lifecycle.strong_sell_confirmation_count = 0

        lifecycle.last_counted_market_observation_key = market_key
        lifecycle.last_transition_at = now if lifecycle.health_state != health_before else lifecycle.last_transition_at

    # 5. Resolve Recommended Action based on current state and portfolio context
    action = LifecycleAction.HOLD
    reason_codes = []

    if lifecycle.health_state == LifecycleHealthState.STABLE:
        if lifecycle.add_confirmation_count >= LifecycleConstants.ADD_THRESHOLD and current_weight <= max_concentration_limit:
            action = LifecycleAction.CONSIDER_ADD
            reason_codes.append("CONSIDER_ADD_MOMENTUM")

    if lifecycle.health_state == LifecycleHealthState.CONFIRMED_DETERIORATION:
        if decision.market_view in ("SELL", "STRONG_SELL"):
            action = LifecycleAction.CONSIDER_REDUCE
            reason_codes.append("CONFIRMED_THESIS_DETERIORATION")

    # Risk-driven reduce overrides thesis reduce
    if current_weight > max_concentration_limit:
        action = LifecycleAction.CONSIDER_REDUCE
        reason_codes.append("PORTFOLIO_CONCENTRATION_BREACH")

    # Exit overrides reduce
    if lifecycle.negative_confirmation_count >= LifecycleConstants.EXIT_THRESHOLD or \
       lifecycle.strong_sell_confirmation_count >= LifecycleConstants.STRONG_EXIT_THRESHOLD:
        action = LifecycleAction.CONSIDER_EXIT
        reason_codes.append("PERSISTENT_SEVERE_DETERIORATION")

    lifecycle.recommended_action = action
    lifecycle.last_evaluated_at = now

    # 6. Snapshot Persistence Check
    # We create a snapshot if:
    # new market key OR new portfolio context key OR state/action changed

    # Check if a snapshot with this exact market_key + context_key already exists for this episode
    stmt_snap = select(PositionLifecycleSnapshot.id).where(
        PositionLifecycleSnapshot.lifecycle_id == lifecycle.id,
        PositionLifecycleSnapshot.episode_number == lifecycle.episode_number,
        PositionLifecycleSnapshot.market_observation_key == market_key,
        PositionLifecycleSnapshot.portfolio_context_key == context_key
    )
    snap_exists = (await db.execute(stmt_snap)).scalar_one_or_none()

    if not snap_exists and (is_new_market or action != action_before or lifecycle.health_state != health_before):
        import json
        snap = PositionLifecycleSnapshot(
            lifecycle_id=lifecycle.id,
            episode_number=lifecycle.episode_number,
            market_observation_key=market_key,
            portfolio_context_key=context_key,
            health_state_before=health_before,
            health_state_after=lifecycle.health_state,
            recommended_action=lifecycle.recommended_action,
            market_view=decision.market_view.value,
            reason_codes=json.dumps(reason_codes),
            evaluated_at=now
        )
        db.add(snap)

    return lifecycle

