from pathlib import Path

p = Path('app/api/v1/endpoints/portfolios.py')
content = p.read_text(encoding='utf-8')

# Ensure UserProfile is imported
content = content.replace('from app.db.models import Instrument, Portfolio, PortfolioTransaction, TradeJournal, User',
                          'from app.db.models import Instrument, Portfolio, PortfolioTransaction, TradeJournal, User, UserProfile')

# Add missing DTO imports
content = content.replace('from app.schemas.portfolio import (',
                          'from app.schemas.portfolio import (\n    BasketPreviewRequest,\n    BasketPreviewResponse,\n    ExecutionPreviewRequest,\n    ExecutionPreviewResponse,\n    ManualTradeCreate,')

# Append endpoints at the end
new_endpoints = '''
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
        
    user_profile = await db.scalar(select(UserProfile).where(UserProfile.id == current_user.id))
        
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
        
    from app.services.scanner import ScannerService
    scanner = ScannerService(registry)
    opps = await scanner.scan_market(db)
    opp = next((o for o in opps if o.instrument_id == instrument.id), None)
    
    analysis_price = opp.current_price if opp else request.manual_native_price
    
    from app.services.fx_service import FxRateService
    fx_service = FxRateService(registry)
    
    fx_rate = Decimal("1.0")
    if instrument.currency == "USD":
        rate = await fx_service.get_usd_try_rate(db)
        if rate:
            fx_rate = rate
        else:
            raise HTTPException(status_code=400, detail="Cannot execute USD trade without FX rate")
            
    return ExecutionPreviewResponse(
        analysis_price=analysis_price,
        analysis_price_state="LIVE" if opp else "UNKNOWN",
        execution_price=request.manual_native_price,
        execution_source="MANUAL",
        execution_currency=instrument.currency,
        fx_rate=fx_rate,
        fx_source="YAHOO",
        fx_as_of=datetime.now(UTC),
        recomputed_quantity=Decimal("0"),
        recomputed_budget=Decimal("0"),
        projected_weight=Decimal("0"),
        market_view=opp.market_view if opp else "NEUTRAL",
        personal_action=opp.personal_action if opp else "HOLD",
        market_score=opp.market_score if opp else 50
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
        rate = await fx_service.get_usd_try_rate(db)
        if rate:
            fx_rate_to_base = rate
        else:
            raise HTTPException(status_code=400, detail="Cannot execute USD trade without FX rate")
            
    base_price = trade_in.native_execution_price * fx_rate_to_base
    
    if trade_in.side == "BUY":
        from app.services.portfolio_ledger import fold_transactions, TransactionData
        all_txs_result = await db.execute(select(PortfolioTransaction).where(PortfolioTransaction.portfolio_id == portfolio.id))
        all_txs = all_txs_result.scalars().all()
        txs_data = [TransactionData(id=t.id, transaction_type=t.transaction_type, instrument_id=t.instrument_id, quantity=t.quantity, price=t.price, fee=t.fee, executed_at=t.executed_at) for t in all_txs]
        state = fold_transactions(txs_data)
        
        total_cost = (base_price * trade_in.quantity) + trade_in.fee
        if state.cash_balance < total_cost:
            raise HTTPException(status_code=400, detail="Insufficient cash for this trade")
            
    if trade_in.side == "SELL":
        from app.services.portfolio_ledger import fold_transactions, TransactionData
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
'''
p.write_text(content + new_endpoints, encoding='utf-8')
