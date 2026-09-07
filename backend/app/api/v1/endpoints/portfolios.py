from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import Instrument, Portfolio, PortfolioTransaction, User
from app.db.session import get_db_session
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioRead,
    PortfolioSummaryDTO,
    PositionDTO,
    TransactionCreate,
    TransactionRead,
)
from app.services.portfolio_ledger import (
    InsufficientCashError,
    InsufficientPositionError,
    InvalidTransactionError,
    TransactionData,
    fold_transactions,
)

router = APIRouter()

@router.post("/", response_model=PortfolioRead)
async def create_portfolio(
    portfolio_in: PortfolioCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    portfolio = Portfolio(**portfolio_in.model_dump(), user_id=current_user.id)
    db.add(portfolio)
    await db.commit()
    await db.refresh(portfolio)
    return portfolio

@router.get("/", response_model=list[PortfolioRead])
async def list_portfolios(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(select(Portfolio).where(Portfolio.user_id == current_user.id))
    return result.scalars().all()

@router.post("/{portfolio_id}/transactions", response_model=TransactionRead)
async def create_transaction(
    portfolio_id: int,
    tx_in: TransactionCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    # Verify portfolio ownership
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id))
    portfolio = result.scalars().first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Validation logic via ledger (to reject oversell/negative cash)
    txs_result = await db.execute(select(PortfolioTransaction).where(PortfolioTransaction.portfolio_id == portfolio_id))
    db_txs = txs_result.scalars().all()

    # Map to service DTO
    ledger_txs = [
        TransactionData(
            id=t.id,
            transaction_type=t.transaction_type,
            instrument_id=t.instrument_id,
            quantity=t.quantity,
            price=t.price,
            fee=t.fee,
            executed_at=t.executed_at
        ) for t in db_txs
    ]

    # Append the tentative new transaction
    executed_time = tx_in.executed_at or datetime.now(UTC)
    tentative_tx = TransactionData(
        id=999999999, # tentative max id
        transaction_type=tx_in.transaction_type,
        instrument_id=tx_in.instrument_id,
        quantity=tx_in.quantity,
        price=tx_in.price,
        fee=tx_in.fee,
        executed_at=executed_time
    )
    ledger_txs.append(tentative_tx)

    try:
        fold_transactions(ledger_txs)
    except (InsufficientCashError, InsufficientPositionError, InvalidTransactionError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Passed math check, commit
    new_tx = PortfolioTransaction(
        portfolio_id=portfolio_id,
        transaction_type=tx_in.transaction_type,
        instrument_id=tx_in.instrument_id,
        quantity=tx_in.quantity,
        price=tx_in.price,
        fee=tx_in.fee,
        executed_at=executed_time,
        notes=tx_in.notes,
        strategy=tx_in.strategy
    )
    db.add(new_tx)
    await db.commit()
    await db.refresh(new_tx)
    return new_tx

@router.get("/{portfolio_id}/summary", response_model=PortfolioSummaryDTO)
async def get_portfolio_summary(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id))
    portfolio = result.scalars().first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    txs_result = await db.execute(select(PortfolioTransaction).where(PortfolioTransaction.portfolio_id == portfolio_id))
    db_txs = txs_result.scalars().all()

    ledger_txs = [
        TransactionData(
            id=t.id,
            transaction_type=t.transaction_type,
            instrument_id=t.instrument_id,
            quantity=t.quantity,
            price=t.price,
            fee=t.fee,
            executed_at=t.executed_at
        ) for t in db_txs
    ]

    state = fold_transactions(ledger_txs)

    # We need to map instrument_id to actual instruments and fetch live quotes to calculate unrealized PNL
    # For Phase 08 MVP, we'll fetch instruments from DB. Quotes integration will be minimal (skip live quotes if not readily available to keep this fast, or use a cached provider).
    # Since we must output null for unavailable prices:

    inst_ids = list(state.positions.keys())
    instruments = {}
    if inst_ids:
        inst_res = await db.execute(select(Instrument).where(Instrument.id.in_(inst_ids)))
        for inst in inst_res.scalars().all():
            instruments[inst.id] = inst

    pos_dtos = []
    total_unrealized = Decimal("0")
    total_market_value = Decimal("0")
    all_prices_live = True

            # Try fetching prices
    for inst_id, pos in state.positions.items():
        if pos.quantity <= 0:
            continue

        inst = instruments.get(inst_id)
        if not inst:
            continue

        # Simplified: no live quote for now, mark as STALE and null
        current_price = None
        market_value = None
        unrealized_pnl = None

        pos_dtos.append(PositionDTO(
            instrument_id=inst_id,
            symbol=inst.symbol,
            name=inst.name,
            quantity=pos.quantity,
            average_cost=pos.average_cost,
            realized_pnl=pos.realized_pnl,
            current_price=current_price,
            market_value=market_value,
            unrealized_pnl=unrealized_pnl
        ))
        all_prices_live = False

    return PortfolioSummaryDTO(
        portfolio_id=portfolio_id,
        cash_balance=state.cash_balance,
        total_deposits=state.total_deposits,
        total_withdrawals=state.total_withdrawals,
        total_realized_pnl=state.total_realized_pnl,
        total_unrealized_pnl=None if not all_prices_live else total_unrealized,
        total_market_value=None if not all_prices_live else total_market_value,
        market_data_freshness="STALE" if not all_prices_live else "LIVE",
        positions=pos_dtos
    )
