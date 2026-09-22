import hashlib
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import PortfolioTransaction
import logging

logger = logging.getLogger(__name__)

async def get_transaction_state_fingerprint(db: AsyncSession, portfolio_id: int) -> str:
    res = await db.execute(
        select(PortfolioTransaction)
        .where(PortfolioTransaction.portfolio_id == portfolio_id)
        .order_by(PortfolioTransaction.executed_at.asc(), PortfolioTransaction.id.asc())
    )
    txs = res.scalars().all()
    
    components = []
    for tx in txs:
        # Canonical representation
        # format: type|instrument|qty|price|fee|native_price|native_cur|fx|executed_at
        qty = f"{tx.quantity:f}" if tx.quantity else "0"
        price = f"{tx.price:f}" if tx.price else "0"
        fee = f"{tx.fee:f}" if tx.fee else "0"
        native_price = f"{tx.native_price:f}" if getattr(tx, 'native_price', None) else ""
        native_cur = tx.native_currency or ""
        fx = f"{tx.execution_fx_rate:f}" if getattr(tx, 'execution_fx_rate', None) else ""
        
        # UTC string format ISO
        exec_at = tx.executed_at.isoformat() if tx.executed_at else ""
        
        comp = f"{tx.transaction_type.value if hasattr(tx.transaction_type, 'value') else tx.transaction_type}|{tx.instrument_id}|{qty}|{price}|{fee}|{native_price}|{native_cur}|{fx}|{exec_at}"
        components.append(comp)
    
    if not components:
        return "EMPTY_LEDGER"
    
    canonical_string = ";".join(components)
    return hashlib.sha256(canonical_string.encode('utf-8')).hexdigest()
