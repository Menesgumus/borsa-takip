from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import (
    Instrument,
    Portfolio,
    PortfolioTransaction,
    TradeJournal,
    User,
    UserProfile,
)
from app.db.session import get_db_session
from app.market.exceptions import ProviderUnavailableError
from app.market.registry import registry
from app.schemas.portfolio import (
    BasketPreviewRequest,
    BasketPreviewResponse,
    ExecutionPreviewRequest,
    ExecutionPreviewResponse,
    ManualTradeCreate,
    PortfolioCreate,
    PortfolioOverviewDTO,
    PortfolioRead,
    PortfolioSummaryDTO,
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
    from app.services.portfolio_valuation import evaluate_portfolios

    result = await db.execute(select(Portfolio).where(Portfolio.user_id == current_user.id))
    portfolios = result.scalars().all()

    valuations = await evaluate_portfolios(db, portfolios)

    overview_dtos = []
    for p in portfolios:
        val = valuations.get(p.id)
        if not val:
            continue
        overview_dtos.append(PortfolioOverviewDTO(
            id=p.id,
            user_id=p.user_id,
            name=p.name,
            portfolio_type=p.portfolio_type,
            currency=p.currency,
            created_at=p.created_at,
            updated_at=p.updated_at,
            cash_balance=val.cash_balance,
            total_realized_pnl=val.total_realized_pnl,
            total_unrealized_pnl=val.total_unrealized_pnl,
            total_market_value=val.total_market_value,
            data_freshness=val.data_freshness,
            valuation_complete=val.valuation_complete
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
    from app.services.portfolio_valuation import evaluate_portfolios

    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id))
    portfolio = result.scalars().first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    valuations = await evaluate_portfolios(db, [portfolio])
    val = valuations.get(portfolio.id)
    if not val:
        raise HTTPException(status_code=500, detail="Valuation failed")

    return PortfolioSummaryDTO(
        portfolio_id=portfolio.id,
        cash_balance=val.cash_balance,
        total_deposits=val.total_deposits,
        total_withdrawals=val.total_withdrawals,
        total_realized_pnl=val.total_realized_pnl,
        total_unrealized_pnl=val.total_unrealized_pnl,
        total_market_value=val.total_market_value,
        market_data_freshness=val.data_freshness,
        valuation_complete=val.valuation_complete,
        positions=val.positions
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
    from app.market.exceptions import ProviderUnavailableError
    from app.market.registry import registry
    from app.services.provider_resolver import resolve_provider

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

    current_prices = {}
    symbols = {}
    provider_symbols: dict[str, list[str]] = {}
    symbol_to_inst_id: dict[str, int] = {}

    for inst_id, inst in instruments.items():
        symbols[inst_id] = inst.symbol
        try:
            resolved = resolve_provider(inst)
            provider_symbols.setdefault(resolved.provider_name, []).append(resolved.provider_symbol)
            symbol_to_inst_id[f"{resolved.provider_name}:{resolved.provider_symbol}"] = inst_id
        except ProviderUnavailableError:
            pass

    for provider_name, symbols_list in provider_symbols.items():
        try:
            results = await registry.get_quotes(provider_name, symbols_list)
            for quote in results:
                i_id = symbol_to_inst_id.get(f"{provider_name}:{quote.symbol}")
                if i_id is not None:
                    current_prices[i_id] = Decimal(str(quote.price))
        except ProviderUnavailableError:
            pass

    risk_metrics = calculate_portfolio_risk(
        state=state,
        current_prices=current_prices,
        symbols=symbols
    )
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
        inst_res = await db.execute(
            select(Instrument)
            .options(selectinload(Instrument.provider_mappings))
            .where(Instrument.id.in_(inst_ids))
        )
        for inst in inst_res.scalars().all():
            instruments[inst.id] = inst

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

    current_prices: dict[int, Decimal] = {}
    for provider_name, symbols_list in provider_symbols.items():
        try:
            results = await registry.get_quotes(provider_name, symbols_list)
            for quote in results:
                i_id = symbol_to_inst_id.get(f"{provider_name}:{quote.symbol}")
                if i_id is not None:
                    current_prices[i_id] = Decimal(str(quote.price))
        except ProviderUnavailableError:
            pass

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

    # 5. Get FX Rate if needed
    from app.services.fx_service import FxRateService
    fx_service = FxRateService(registry)
    fx_rate_to_base = Decimal("1.0")
    if inst.currency == "USD":
        fx_res = await fx_service.get_usd_try_rate(db)
        if fx_res:
            fx_rate_to_base = fx_res.rate
        else:
            raise HTTPException(status_code=400, detail="Cannot execute USD trade without FX rate")

    native_execution_price = Decimal(str(quote.price))
    execution_base_price = native_execution_price * fx_rate_to_base
    execution_price = execution_base_price
    quantity = Decimal("0")

    # 6. Determine quantity if budget mode
    if trade_in.side == "BUY":
        if trade_in.budget_amount is not None and trade_in.budget_amount > 0:
            quantity = trade_in.budget_amount // execution_base_price
            if quantity < 1:
                raise HTTPException(status_code=400, detail="Bu tutarla en az 1 adet hisse alınamıyor.")
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
        executed_at=datetime.now(UTC),
        native_price=native_execution_price,
        native_currency=inst.currency,
        fx_rate_to_base=fx_rate_to_base,
        execution_source="SYSTEM_QUOTE"
    )
    db.add(new_tx)
    await db.commit()
    await db.refresh(new_tx)

    # Manually attach symbol for response
    new_tx.instrument_symbol = inst.symbol
    return new_tx

from app.services.basket_service import BasketBuilderService


@router.post("/{portfolio_id}/basket-preview", response_model=BasketPreviewResponse)
async def preview_basket(
    portfolio_id: int,
    request: BasketPreviewRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    portfolio = await db.scalar(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id))
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    if request.deploy_amount <= 0:
        raise HTTPException(status_code=400, detail="Deploy amount must be positive")

    user_profile = await db.scalar(select(UserProfile).where(UserProfile.user_id == current_user.id))

    service = BasketBuilderService(registry)
    return await service.build_basket(db, portfolio_id, request.deploy_amount, user_profile)

@router.post("/{portfolio_id}/execution-preview", response_model=ExecutionPreviewResponse)
async def preview_execution(
    portfolio_id: int,
    request: ExecutionPreviewRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    portfolio = await db.scalar(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id))
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    instrument = await db.scalar(select(Instrument).where(Instrument.id == request.instrument_id))
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")

    from app.services.scanner import scan_opportunities
    opps = await scan_opportunities(db, current_user, portfolio_id, symbols=[instrument.symbol])
    opp = opps[0] if opps else None
    
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not actionable or missing data")

    from app.services.fx_service import FxRateService
    fx_service = FxRateService(registry)

    fx_rate = Decimal("1.0")
    fx_source = "NONE"
    fx_as_of = datetime.now(UTC)
    
    if instrument.currency == "USD":
        fx_res = await fx_service.get_usd_try_rate(db)
        if fx_res:
            fx_rate = fx_res.rate
            fx_source = fx_res.source
            fx_as_of = fx_res.as_of
        else:
            raise HTTPException(status_code=400, detail="Cannot execute USD trade without FX rate")

    # Evaluate portfolio
    from app.services.portfolio_valuation import evaluate_portfolios
    evals = await evaluate_portfolios(db, [portfolio])
    val = evals.get(portfolio_id)
    if not val or not val.valuation_complete:
        raise HTTPException(status_code=400, detail="Portfolio valuation incomplete")

    available_cash = val.cash_balance
    total_value = available_cash + (val.invested_market_value or Decimal("0"))

    # Current position
    current_quantity = 0
    if val.positions:
        pos = next((p for p in val.positions if p["instrument_id"] == instrument.id), None)
        if pos:
            current_quantity = int(pos.get("quantity", 0))

    from app.services.position_sizing import calculate_position_sizing
    from app.schemas.decision import DecisionAction

    execution_base_price = request.manual_native_price * fx_rate
    
    action_str = opp.personal_action if opp.personal_action else opp.market_view
    action_enum = DecisionAction(action_str)

    p_res = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = p_res.scalars().first()
    risk_tol = profile.risk_tolerance.value if profile and profile.risk_tolerance else "MEDIUM"

    sizing = calculate_position_sizing(
        available_cash=available_cash,
        total_portfolio_value=total_value,
        current_price=execution_base_price,
        current_quantity=current_quantity,
        market_view=DecisionAction(opp.market_view),
        personal_action=DecisionAction(opp.personal_action) if opp.personal_action else None,
        data_state="MANUAL_BROKER",
        hard_limit=Decimal("0.30"),
        risk_tolerance=risk_tol
    )

    return ExecutionPreviewResponse(
        analysis_price=opp.quote_price or Decimal("0"),
        analysis_price_state=opp.quote_data_state or "UNKNOWN",
        execution_price=request.manual_native_price,
        execution_source="MANUAL_BROKER",
        execution_currency=instrument.currency,
        fx_rate=fx_rate,
        fx_source=fx_source,
        fx_as_of=fx_as_of,
        recomputed_quantity=Decimal(sizing.recommended_quantity),
        recomputed_budget=sizing.recommended_budget or Decimal("0"),
        projected_weight=sizing.estimated_post_trade_weight or Decimal("0"),
        market_view=opp.market_view,
        personal_action=opp.personal_action,
        market_score=opp.market_score or 50
    )

@router.post("/{portfolio_id}/manual-trade", response_model=TransactionRead)
async def execute_manual_trade(
    portfolio_id: int,
    trade_in: ManualTradeCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    portfolio = await db.scalar(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id))
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    if portfolio.portfolio_type != "REAL":
        raise HTTPException(status_code=400, detail="Manual trades are only allowed for REAL portfolios")

    if trade_in.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    if trade_in.native_execution_price <= 0:
        raise HTTPException(status_code=400, detail="Price must be positive")
    if trade_in.fee < 0:
        raise HTTPException(status_code=400, detail="Fee cannot be negative")

    instrument = await db.scalar(select(Instrument).where(Instrument.id == trade_in.instrument_id))
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")

    from app.services.fx_service import FxRateService
    fx_service = FxRateService(registry)

    fx_rate_to_base = Decimal("1.0")
    if instrument.currency == "USD":
        rate_res = await fx_service.get_usd_try_rate(db)
        if rate_res:
            fx_rate_to_base = rate_res.rate
        else:
            raise HTTPException(status_code=400, detail="Cannot execute USD trade without FX rate")

    base_price = trade_in.native_execution_price * fx_rate_to_base

    if trade_in.side == "BUY":
        from app.services.portfolio_ledger import TransactionData, fold_transactions
        all_txs_result = await db.execute(select(PortfolioTransaction).where(PortfolioTransaction.portfolio_id == portfolio.id))
        all_txs = all_txs_result.scalars().all()
        txs_data = [TransactionData(id=t.id, transaction_type=t.transaction_type, instrument_id=t.instrument_id, quantity=t.quantity, price=t.price, fee=t.fee, executed_at=t.executed_at) for t in all_txs]
        state = fold_transactions(txs_data)

        total_cost = (base_price * trade_in.quantity) + trade_in.fee
        if state.cash_balance < total_cost:
            raise HTTPException(status_code=400, detail="Insufficient cash for this trade")

    if trade_in.side == "SELL":
        from app.services.portfolio_ledger import TransactionData, fold_transactions
        all_txs_result = await db.execute(select(PortfolioTransaction).where(PortfolioTransaction.portfolio_id == portfolio.id))
        all_txs = all_txs_result.scalars().all()
        txs_data = [TransactionData(id=t.id, transaction_type=t.transaction_type, instrument_id=t.instrument_id, quantity=t.quantity, price=t.price, fee=t.fee, executed_at=t.executed_at) for t in all_txs]
        state = fold_transactions(txs_data)
        pos = state.positions.get(instrument.id)
        if not pos or pos.quantity < trade_in.quantity:
            raise HTTPException(status_code=400, detail="Insufficient position quantity for this trade")

    transaction_type = "BUY" if trade_in.side == "BUY" else "SELL"

    tx = PortfolioTransaction(
        portfolio_id=portfolio.id,
        transaction_type=transaction_type,
        instrument_id=instrument.id,
        quantity=trade_in.quantity,
        price=base_price,
        fee=trade_in.fee,
        native_price=trade_in.native_execution_price,
        native_currency=instrument.currency,
        fx_rate_to_base=fx_rate_to_base,
        execution_source="MANUAL_BROKER",
        executed_at=trade_in.executed_at or datetime.now(UTC)
    )
    db.add(tx)
    await db.commit()
    await db.refresh(tx)

    return tx
