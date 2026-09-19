from pathlib import Path

# 1. Fix Basket Service (remove market_score >= 70 eligibility gate, allow STRONG_BUY)
basket_path = Path('app/services/basket_service.py')
basket_content = basket_path.read_text(encoding='utf-8')
basket_content = basket_content.replace(
    'actionable = [o for o in opportunities if o.market_score >= 70 and o.personal_action == "BUY"]',
    'actionable = [o for o in opportunities if o.personal_action in ("BUY", "STRONG_BUY")]'
)
basket_path.write_text(basket_content, encoding='utf-8')

# 2. Fix Portfolios Endpoints (Add REAL portfolio check, positive quantity/price check, cash check)
portfolios_path = Path('app/api/v1/endpoints/portfolios.py')
portfolios_content = portfolios_path.read_text(encoding='utf-8')

manual_trade_validation = '''
    if portfolio.portfolio_type != "REAL":
        raise HTTPException(status_code=400, detail="Manual trades are only allowed for REAL portfolios")
        
    if trade_in.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    if trade_in.native_execution_price <= 0:
        raise HTTPException(status_code=400, detail="Price must be positive")
    if trade_in.fee < 0:
        raise HTTPException(status_code=400, detail="Fee cannot be negative")
'''

portfolios_content = portfolios_content.replace(
    'if not instrument:\n        raise HTTPException(status_code=404, detail="Instrument not found")',
    'if not instrument:\n        raise HTTPException(status_code=404, detail="Instrument not found")\n' + manual_trade_validation
)

# Also check cash balance before executing BUY in manual trade
cash_check = '''
    base_price = trade_in.native_execution_price * fx_rate_to_base
    
    if trade_in.side == "BUY":
        from app.services.portfolio_ledger import fold_transactions, TransactionData
        all_txs_result = await db.execute(select(PortfolioTransaction).where(PortfolioTransaction.portfolio_id == portfolio.id))
        all_txs = all_txs_result.scalars().all()
        
        txs_data = [TransactionData(
            id=t.id,
            transaction_type=t.transaction_type,
            instrument_id=t.instrument_id,
            quantity=t.quantity,
            price=t.price,
            fee=t.fee,
            executed_at=t.executed_at
        ) for t in all_txs]
        state = fold_transactions(txs_data)
        
        total_cost = (base_price * trade_in.quantity) + trade_in.fee
        if state.cash_balance < total_cost:
            raise HTTPException(status_code=400, detail="Insufficient cash for this trade")
            
    # Sell position check
    if trade_in.side == "SELL":
        from app.services.portfolio_ledger import fold_transactions, TransactionData
        all_txs_result = await db.execute(select(PortfolioTransaction).where(PortfolioTransaction.portfolio_id == portfolio.id))
        all_txs = all_txs_result.scalars().all()
        txs_data = [TransactionData(id=t.id, transaction_type=t.transaction_type, instrument_id=t.instrument_id, quantity=t.quantity, price=t.price, fee=t.fee, executed_at=t.executed_at) for t in all_txs]
        state = fold_transactions(txs_data)
        pos = state.positions.get(instrument.id)
        if not pos or pos.quantity < trade_in.quantity:
            raise HTTPException(status_code=400, detail="Insufficient position quantity for this trade")
'''
portfolios_content = portfolios_content.replace(
    'base_price = trade_in.native_execution_price * fx_rate_to_base\n    \n    transaction_type = "BUY" if trade_in.side == "BUY" else "SELL"',
    cash_check + '\n    transaction_type = "BUY" if trade_in.side == "BUY" else "SELL"'
)

# Prevent Basket Preview with <= 0 deploy amount
preview_validation = '''
    if request.deploy_amount <= 0:
        raise HTTPException(status_code=400, detail="Deploy amount must be positive")
'''
portfolios_content = portfolios_content.replace(
    'if not portfolio:\n        raise HTTPException(status_code=404, detail="Portfolio not found")',
    'if not portfolio:\n        raise HTTPException(status_code=404, detail="Portfolio not found")\n' + preview_validation
)

portfolios_path.write_text(portfolios_content, encoding='utf-8')
