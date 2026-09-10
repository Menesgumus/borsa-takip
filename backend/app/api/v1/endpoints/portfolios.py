from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import Instrument, Portfolio, PortfolioTransaction, TradeJournal, User
from app.db.session import get_db_session
from app.market.exceptions import ProviderUnavailableError
from app.market.registry import registry
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioOverviewDTO,
    PortfolioRead,
    PortfolioSummaryDTO,
    PositionDTO,
    TradeJournalCreate,
    TradeJournalRead,
    TransactionCreate,
    TransactionRead,
)
from app.schemas.risk import PortfolioRiskMetrics, WhatIfRequest, WhatIfResponse
from app.services.portfolio_ledger import (
    InsufficientCashError,
    InsufficientPositionError,
    InvalidTransactionError,
    TransactionData,
    fold_transactions,
)
from app.services.provider_resolver import resolve_provider

router = APIRouter()

@router.post("", response_model=PortfolioRead)
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

@router.get("", response_model=list[PortfolioOverviewDTO])
async def list_portfolios(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(select(Portfolio).where(Portfolio.user_id == current_user.id))
    portfolios = result.scalars().all()

    overview_dtos = []
    for p in portfolios:
        txs_result = await db.execute(select(PortfolioTransaction).where(PortfolioTransaction.portfolio_id == p.id))
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

        overview_dtos.append(PortfolioOverviewDTO(
            id=p.id,
            user_id=p.user_id,
            name=p.name,
            portfolio_type=p.portfolio_type,
            currency=p.currency,
            created_at=p.created_at,
            updated_at=p.updated_at,
            total_realized_pnl=state.total_realized_pnl,
            total_market_value=None  # We don't fetch live quotes in the list view for MVP
        ))

    return overview_dtos

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

@router.get("/{portfolio_id}/transactions", response_model=list[TransactionRead])
async def get_portfolio_transactions(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id))
    portfolio = result.scalars().first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    txs_result = await db.execute(
        select(PortfolioTransaction)
        .options(selectinload(PortfolioTransaction.instrument))
        .where(PortfolioTransaction.portfolio_id == portfolio_id)
        .order_by(PortfolioTransaction.executed_at.desc())
    )

    txs = txs_result.scalars().all()
    results = []
    for tx in txs:
        tx_dict = {
            "id": tx.id,
            "portfolio_id": tx.portfolio_id,
            "transaction_type": tx.transaction_type,
            "instrument_id": tx.instrument_id,
            "quantity": tx.quantity,
            "price": tx.price,
            "fee": tx.fee,
            "executed_at": tx.executed_at,
            "created_at": tx.created_at,
            "notes": tx.notes,
            "strategy": tx.strategy,
            "instrument_symbol": tx.instrument.symbol if tx.instrument else None
        }
        results.append(tx_dict)

    return results

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
        inst_res = await db.execute(
            select(Instrument)
            .options(selectinload(Instrument.provider_mappings))
            .where(Instrument.id.in_(inst_ids))
        )
        for inst in inst_res.scalars().all():
            instruments[inst.id] = inst

    pos_dtos = []
    total_unrealized = Decimal("0")
    total_market_value = Decimal("0")
    all_prices_live = True

    # Batch gather quotes for performance if multiple symbols exist
    # Group by provider
    provider_symbols: dict[str, list[str]] = {}
    symbol_to_inst_id: dict[str, int] = {}
    for inst_id in inst_ids:
        inst = instruments.get(inst_id)
        if inst:
            try:
                resolved = resolve_provider(inst)
                provider_symbols.setdefault(resolved.provider_name, []).append(resolved.provider_symbol)
                symbol_to_inst_id[f"{resolved.provider_name}:{resolved.provider_symbol}"] = inst_id
            except ProviderUnavailableError:
                pass

    quotes: dict[int, Decimal] = {}
    for provider_name, symbols in provider_symbols.items():
        try:
            results = await registry.get_quotes(provider_name, symbols)
            for quote in results:
                inst_id = symbol_to_inst_id.get(f"{provider_name}:{quote.symbol}")
                if inst_id is not None:
                    quotes[inst_id] = Decimal(str(quote.price))
        except ProviderUnavailableError:
            pass

    for inst_id, pos in state.positions.items():
        if pos.quantity <= 0:
            continue

        inst = instruments.get(inst_id)
        if not inst:
            continue

        current_price = quotes.get(inst_id)
        market_value = None
        unrealized_pnl = None

        if current_price is not None:
            market_value = pos.quantity * current_price
            cost_basis = pos.quantity * pos.average_cost
            unrealized_pnl = market_value - cost_basis

            total_market_value += market_value
            total_unrealized += unrealized_pnl
        else:
            all_prices_live = False

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

    # Add cash to total market value
    if all_prices_live:
        total_market_value += state.cash_balance

    return PortfolioSummaryDTO(
        portfolio_id=portfolio_id,
        cash_balance=state.cash_balance,
        total_deposits=state.total_deposits,
        total_withdrawals=state.total_withdrawals,
        total_realized_pnl=state.total_realized_pnl,
        total_unrealized_pnl=None if not all_prices_live else total_unrealized,
        total_market_value=None if not all_prices_live else total_market_value,
        market_data_freshness="STALE" if not all_prices_live else "DELAYED",
        positions=pos_dtos
    )


@router.post("/{portfolio_id}/journals", response_model=TradeJournalRead)
async def create_trade_journal(
    portfolio_id: int,
    journal_in: TradeJournalCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Portfolio not found")

    journal = TradeJournal(**journal_in.model_dump(), portfolio_id=portfolio_id)
    db.add(journal)
    await db.commit()
    await db.refresh(journal)
    return journal

@router.get("/{portfolio_id}/journals", response_model=list[TradeJournalRead])
async def list_trade_journals(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Portfolio not found")

    result = await db.execute(select(TradeJournal).where(TradeJournal.portfolio_id == portfolio_id))
    return result.scalars().all()


from app.services.portfolio_risk import calculate_portfolio_risk, simulate_what_if


@router.get("/{portfolio_id}/risk", response_model=PortfolioRiskMetrics)
async def get_portfolio_risk(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id))
    if not result.scalars().first():
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

    from app.services.portfolio_ledger import fold_transactions
    state = fold_transactions(ledger_txs)

    inst_ids = list(state.positions.keys())
    instruments = {}
    if inst_ids:
        inst_res = await db.execute(select(Instrument).where(Instrument.id.in_(inst_ids)))
        for inst in inst_res.scalars().all():
            instruments[inst.id] = inst

    # For Phase 09, we assume current prices are None to test partial coverage / stale handling
    # Unless we fetch them from a mock provider
    current_prices = {}
    symbols = {i_id: i.symbol for i_id, i in instruments.items()}

    risk_metrics = calculate_portfolio_risk(state, current_prices, symbols)
    risk_metrics.portfolio_id = portfolio_id
    return risk_metrics

@router.post("/{portfolio_id}/what-if", response_model=WhatIfResponse)
async def portfolio_what_if(
    portfolio_id: int,
    request: WhatIfRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id))
    if not result.scalars().first():
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

    from app.services.portfolio_ledger import fold_transactions
    state = fold_transactions(ledger_txs)
    inst_ids = list(state.positions.keys())
    if request.instrument_id not in inst_ids:
        inst_ids.append(request.instrument_id)

    instruments = {}
    if inst_ids:
        inst_res = await db.execute(select(Instrument).where(Instrument.id.in_(inst_ids)))
        for inst in inst_res.scalars().all():
            instruments[inst.id] = inst

    current_prices = {}
    symbols = {i_id: i.symbol for i_id, i in instruments.items()}

    sim_tx = TransactionData(
        id=999999,
        transaction_type=request.transaction_type,
        instrument_id=request.instrument_id,
        quantity=request.quantity,
        price=request.price,
        fee=request.fee,
        executed_at=datetime.now(UTC)
    )

    # We catch Ledger errors (like Insufficient Cash in What-If)
    from app.services.portfolio_ledger import (
        InsufficientCashError,
        InsufficientPositionError,
        InvalidTransactionError,
    )
    try:
        resp = simulate_what_if(ledger_txs, sim_tx, current_prices, symbols)
    except (InsufficientCashError, InsufficientPositionError, InvalidTransactionError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    resp.before_risk.portfolio_id = portfolio_id
    resp.after_risk.portfolio_id = portfolio_id
    return resp

import math

from app.db.models import PortfolioType, TransactionType
from app.schemas.portfolio import PortfolioTradeCreate


@router.post("/{portfolio_id}/trade", response_model=TransactionRead)
async def execute_trade(
    portfolio_id: int,
    trade_in: PortfolioTradeCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    # 1. Verify portfolio ownership & type
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id))
    portfolio = result.scalars().first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if portfolio.portfolio_type != PortfolioType.PAPER:
        raise HTTPException(status_code=400, detail="Endpoint only supports PAPER portfolios")

    # 2. Load instrument
    inst = await db.get(Instrument, trade_in.instrument_id, options=[selectinload(Instrument.provider_mappings)])
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")

    # 3. Resolve canonical provider
    try:
        resolved = resolve_provider(inst)
    except ProviderUnavailableError:
        raise HTTPException(status_code=400, detail="No provider mapping configured")

    # 4. Fetch quote
    try:
        results = await registry.get_quotes(resolved.provider_name, [resolved.provider_symbol])
        if not results:
            raise ProviderUnavailableError(resolved.provider_name, "Empty quote result")
        quote = results[0]
    except ProviderUnavailableError:
        raise HTTPException(status_code=400, detail="Fiyat alınamadı (Provider Unavailable)")

    # 5. Validate quote state
    if quote.data_state in ["UNAVAILABLE", "PROVIDER_ERROR", "TIMEOUT", "NOT_FOUND"]:
        raise HTTPException(status_code=400, detail="Fiyat alınamadı veya veriler çok eski")
    if quote.price is None or quote.price <= 0:
        raise HTTPException(status_code=400, detail="Geçersiz fiyat verisi")

    execution_price = Decimal(str(quote.price))
    quantity = Decimal("0")

    # 6. Determine quantity if budget mode
    if trade_in.side == "BUY":
        if trade_in.budget_amount is not None and trade_in.budget_amount > 0:
            qty_float = math.floor(float(trade_in.budget_amount) / float(execution_price))
            if qty_float < 1:
                raise HTTPException(status_code=400, detail="Bu tutarla en az 1 adet hisse alınamıyor.")
            quantity = Decimal(str(qty_float))
        elif trade_in.quantity is not None and trade_in.quantity > 0:
            quantity = trade_in.quantity
        else:
            raise HTTPException(status_code=400, detail="Adet veya tutar belirtilmelidir")
    else: # SELL
        if trade_in.quantity is None or trade_in.quantity <= 0:
            raise HTTPException(status_code=400, detail="Satış için adet belirtilmelidir")
        quantity = trade_in.quantity

    # 7. Validate cash/position via fold_transactions
    tx_type = TransactionType.BUY if trade_in.side == "BUY" else TransactionType.SELL

    txs_result = await db.execute(select(PortfolioTransaction).where(PortfolioTransaction.portfolio_id == portfolio_id))
    db_txs = txs_result.scalars().all()
    ledger_txs = [
        TransactionData(
            id=t.id, transaction_type=t.transaction_type, instrument_id=t.instrument_id,
            quantity=t.quantity, price=t.price, fee=t.fee, executed_at=t.executed_at
        ) for t in db_txs
    ]

    sim_tx = TransactionData(
        id=999999, transaction_type=tx_type, instrument_id=trade_in.instrument_id,
        quantity=quantity, price=execution_price, fee=Decimal("0"), executed_at=datetime.now(UTC)
    )
    ledger_txs.append(sim_tx)

    try:
        fold_transactions(ledger_txs)
    except InsufficientCashError:
        raise HTTPException(status_code=400, detail="Yetersiz bakiye")
    except InsufficientPositionError:
        raise HTTPException(status_code=400, detail="Yetersiz hisse senedi")
    except InvalidTransactionError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 8. Create Transaction
    new_tx = PortfolioTransaction(
        portfolio_id=portfolio_id,
        transaction_type=tx_type,
        instrument_id=trade_in.instrument_id,
        quantity=quantity,
        price=execution_price,
        fee=Decimal("0"),
        executed_at=datetime.now(UTC)
    )
    db.add(new_tx)
    await db.commit()
    await db.refresh(new_tx)

    # Manually attach symbol for response
    new_tx.instrument_symbol = inst.symbol
    return new_tx
