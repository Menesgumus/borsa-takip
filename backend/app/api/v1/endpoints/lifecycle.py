import json
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import (
    AssetClass,
    Instrument,
    Portfolio,
    PositionLifecycle,
    PositionLifecycleSnapshot,
    User,
)
from app.db.session import get_db_session
from app.schemas.lifecycle import LifecycleSnapshotDTO, PositionLifecycleDTO
from app.services.lifecycle_engine import (
    LifecycleAction,
    LifecycleHealthState,
    evaluate_lifecycle_for_instrument,
    process_position_lifecycle,
)
from app.services.portfolio_valuation import evaluate_portfolios

router = APIRouter()

@router.post("/evaluate", response_model=list[PositionLifecycleDTO])
async def evaluate_lifecycle(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    # 1. Authorize
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
    portfolio = result.scalar_one_or_none()
    if not portfolio or portfolio.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # 2. Compute Valuation
    val_map = await evaluate_portfolios(db, [portfolio])
    val = val_map.get(portfolio.id)
    if not val:
        raise HTTPException(status_code=500, detail="Could not value portfolio")

    cash_balance = val.cash_balance
    is_valuation_complete = val.valuation_complete

    # Pre-fetch instruments to avoid N+1 inside the loop
    inst_ids = [p["instrument_id"] for p in val.positions]
    instruments = {}
    if inst_ids:
        res = await db.execute(select(Instrument).where(Instrument.id.in_(inst_ids)))
        for inst in res.scalars():
            instruments[inst.id] = inst

    # max concentration is typically 0.3 for equities, let's use a safe fallback or fetch from portfolio risk


    # Get transaction state version
    from app.services.fingerprint import get_transaction_state_fingerprint
    transaction_state_version = await get_transaction_state_fingerprint(db, portfolio_id)

    # 3. Process Each Position
    lifecycles = []

    for p_dict in val.positions:
        inst_id = p_dict["instrument_id"]
        if inst_id not in instruments:
            continue

        inst = instruments[inst_id]
        if inst.asset_class == AssetClass.FX_REFERENCE:
            continue # Skip FX

        qty = Decimal(str(p_dict["quantity"]))
        weight = Decimal(str(p_dict.get("current_weight", "0") or "0"))

        # Hard limit
        limit_pct = Decimal("0.30")

        # Extract canonical FX rate from valuation dictionary
        fx_rate = p_dict.get("current_fx_rate_to_base")
        if inst.currency == "TRY":
            fx_rate_val = Decimal("1.0")
            is_evaluable_context = is_valuation_complete
        elif fx_rate is not None:
            fx_rate_val = Decimal(str(fx_rate))
            is_evaluable_context = is_valuation_complete
        else:
            is_evaluable_context = False
            fx_rate_val = None

        decision, market_key, context_key_partial, is_evaluable = await evaluate_lifecycle_for_instrument(
            db, current_user, portfolio, inst, qty, weight, cash_balance, limit_pct, is_evaluable_context, fx_rate_val, transaction_state_version
        )

        # Lock and Process State Machine
        lifecycle = await process_position_lifecycle(
            db, portfolio.id, inst.id, qty, weight, limit_pct, decision, market_key, context_key_partial, is_evaluable
        )

        # Build DTO
        dto = PositionLifecycleDTO.model_validate(lifecycle)
        dto.symbol = inst.symbol
        dto.asset_class = str(inst.asset_class)
        dto.native_currency = inst.currency
        dto.is_evaluable = is_evaluable
        dto.data_state = "COMPLETED" if is_evaluable else "NO_ACTION_DATA"

        dto.current_quantity = qty
        avg_c = p_dict.get("average_cost")
        dto.average_cost_base = Decimal(str(avg_c)) if avg_c is not None else None

        val_base = p_dict.get("market_value")
        dto.current_market_value_base = Decimal(str(val_base)) if val_base is not None else None

        upl = p_dict.get("unrealized_pnl")
        dto.unrealized_pnl_base = Decimal(str(upl)) if upl is not None else None

        upl_pct = p_dict.get("unrealized_pnl_pct")
        dto.unrealized_pnl_pct = Decimal(str(upl_pct)) if upl_pct is not None else None

        dto.current_weight = weight

        dto.market_score = decision.overall_personal_score
        dto.technical_score = decision.technical_score
        dto.fundamental_score = decision.fundamental_score
        dto.data_quality_score = decision.data_quality_score

        if lifecycle.recommended_action == LifecycleAction.CONSIDER_REDUCE:
            from app.services.reduce_helper import calculate_reduce_quantity
            dto.suggested_reduce_quantity = calculate_reduce_quantity(qty, Decimal("0.5"))
        elif lifecycle.recommended_action == LifecycleAction.CONSIDER_EXIT:
            dto.suggested_reduce_quantity = qty

        if dto.suggested_reduce_quantity is not None:
            dto.suggested_remaining_quantity = qty - dto.suggested_reduce_quantity
            # preview proceeds
            price = Decimal(str(p_dict.get("current_price") or "0"))
            fx = Decimal(str(p_dict.get("current_fx_rate_to_base") or "1"))
            dto.estimated_released_cash_base = dto.suggested_reduce_quantity * price * fx

        from app.schemas.lifecycle import LifecycleEvidence
        # Re-fetch the snap to populate reason codes correctly in the DTO if it was just saved
        dto.evidence = LifecycleEvidence(
            market_view=decision.market_view.value,
            reason_codes=[] # Will be hydrated from snapshot if needed, or we can just infer
        )

        # Actually the snapshot reason codes are JSON
        stmt = select(PositionLifecycleSnapshot).where(PositionLifecycleSnapshot.lifecycle_id == lifecycle.id).order_by(PositionLifecycleSnapshot.evaluated_at.desc()).limit(1)
        snap = (await db.execute(stmt)).scalar_one_or_none()
        if snap and snap.reason_codes:
            dto.evidence.reason_codes = json.loads(snap.reason_codes)

        lifecycles.append(dto)


    # Find active lifecycles that are no longer in the valuation (closed positions)
    active_stmt = select(PositionLifecycle).where(
        PositionLifecycle.portfolio_id == portfolio.id,
        PositionLifecycle.health_state != LifecycleHealthState.CLOSED
    )
    active_lcs = (await db.execute(active_stmt)).scalars().all()
    active_inst_ids = [lc.instrument_id for lc in active_lcs]

    val_inst_ids = set([p["instrument_id"] for p in val.positions if Decimal(str(p["quantity"])) > 0])

    for lc in active_lcs:
        if lc.instrument_id not in val_inst_ids:
            # Position was closed
            lc.health_state = LifecycleHealthState.CLOSED
            lc.recommended_action = LifecycleAction.HOLD

            lc.negative_confirmation_count = 0
            lc.add_confirmation_count = 0
            lc.updated_at = datetime.utcnow()

    await db.commit()
    return lifecycles

@router.get("", response_model=list[PositionLifecycleDTO])
async def get_lifecycle(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    # GET is Read Only. Just fetches existing lifecycles.
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
    portfolio = result.scalar_one_or_none()
    if not portfolio or portfolio.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    val_map = await evaluate_portfolios(db, [portfolio])
    val = val_map.get(portfolio.id)
    if not val:
        raise HTTPException(status_code=500, detail="Could not value portfolio")

    stmt = select(PositionLifecycle, Instrument).join(Instrument).where(PositionLifecycle.portfolio_id == portfolio_id)
    records = (await db.execute(stmt)).all()

    lifecycles = []

    # Map by instrument id
    p_dict_map = {p["instrument_id"]: p for p in val.positions}

    for lc, inst in records:
        # If not open, maybe skip? Let's return open ones
        if lc.health_state == LifecycleHealthState.CLOSED:
            continue

        p_dict = p_dict_map.get(inst.id, {})
        qty = Decimal(str(p_dict.get("quantity", "0")))
        if qty == 0:
            continue

        dto = PositionLifecycleDTO.model_validate(lc)
        dto.symbol = inst.symbol
        dto.asset_class = str(inst.asset_class)
        dto.native_currency = inst.currency

        dto.current_quantity = qty
        avg_c = p_dict.get("average_cost")
        dto.average_cost_base = Decimal(str(avg_c)) if avg_c is not None else None

        val_base = p_dict.get("market_value")
        dto.current_market_value_base = Decimal(str(val_base)) if val_base is not None else None

        upl = p_dict.get("unrealized_pnl")
        dto.unrealized_pnl_base = Decimal(str(upl)) if upl is not None else None

        upl_pct = p_dict.get("unrealized_pnl_pct")
        dto.unrealized_pnl_pct = Decimal(str(upl_pct)) if upl_pct is not None else None

        dto.current_weight = Decimal(str(p_dict.get("current_weight", "0") or "0"))

        if lc.recommended_action == LifecycleAction.CONSIDER_REDUCE:
            from app.services.reduce_helper import calculate_reduce_quantity
            dto.suggested_reduce_quantity = calculate_reduce_quantity(qty, Decimal("0.5"))
        elif lc.recommended_action == LifecycleAction.CONSIDER_EXIT:
            dto.suggested_reduce_quantity = qty

        if dto.suggested_reduce_quantity is not None:
            dto.suggested_remaining_quantity = qty - dto.suggested_reduce_quantity
            price = Decimal(str(p_dict.get("current_price") or "0"))
            fx = Decimal(str(p_dict.get("current_fx_rate_to_base") or "1"))
            dto.estimated_released_cash_base = dto.suggested_reduce_quantity * price * fx

        # Add basic evidence info
        from app.schemas.lifecycle import LifecycleEvidence
        dto.evidence = LifecycleEvidence()
        snap_stmt = select(PositionLifecycleSnapshot).where(PositionLifecycleSnapshot.lifecycle_id == lc.id).order_by(PositionLifecycleSnapshot.evaluated_at.desc()).limit(1)
        snap = (await db.execute(snap_stmt)).scalar_one_or_none()
        if snap:
            dto.evidence.market_view = snap.market_view
            if snap.reason_codes:
                dto.evidence.reason_codes = json.loads(snap.reason_codes)

        lifecycles.append(dto)

    return lifecycles

@router.get("/positions/{instrument_id}", response_model=list[LifecycleSnapshotDTO])
async def get_lifecycle_history(
    portfolio_id: int,
    instrument_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
    portfolio = result.scalar_one_or_none()
    if not portfolio or portfolio.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    stmt = select(PositionLifecycle).where(
        PositionLifecycle.portfolio_id == portfolio_id,
        PositionLifecycle.instrument_id == instrument_id
    )
    lc = (await db.execute(stmt)).scalar_one_or_none()

    if not lc:
        return []

    snap_stmt = select(PositionLifecycleSnapshot).where(
        PositionLifecycleSnapshot.lifecycle_id == lc.id
    ).order_by(PositionLifecycleSnapshot.evaluated_at.desc()).limit(50)

    snaps = (await db.execute(snap_stmt)).scalars().all()

    return [LifecycleSnapshotDTO.model_validate(s) for s in snaps]
