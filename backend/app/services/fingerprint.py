import hashlib
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.db.models import PortfolioTransaction
import logging
from app.services.canonical import canonicalize

logger = logging.getLogger(__name__)

async def get_transaction_state_fingerprint(db: AsyncSession, portfolio_id: int) -> str:
    res = await db.execute(
        select(PortfolioTransaction)
        .options(joinedload(PortfolioTransaction.instrument))
        .where(PortfolioTransaction.portfolio_id == portfolio_id)
        # We fetch all, then sort in python to avoid DB-specific sort logic dependencies for semantic order
    )
    txs = res.scalars().all()
    
    components = []
    for tx in txs:
        # Canonical instrument
        if tx.instrument:
            inst_canon = f"{tx.instrument.exchange}|{tx.instrument.symbol}|{tx.instrument.asset_class.value if hasattr(tx.instrument.asset_class, 'value') else tx.instrument.asset_class}|{tx.instrument.currency}"
        else:
            inst_canon = "NONE"
            
        comp = (
            canonicalize(tx.executed_at),
            canonicalize(tx.transaction_type),
            inst_canon,
            canonicalize(tx.quantity),
            canonicalize(tx.price),
            canonicalize(tx.fee),
            canonicalize(tx.native_price),
            canonicalize(tx.native_currency),
            canonicalize(tx.fx_rate_to_base),
            canonicalize(tx.execution_source)
        )
        components.append(comp)
    
    if not components:
        return "EMPTY_LEDGER"
        
    # Sort deterministically by all fields to ensure order independence from DB id
    components.sort()
    
    # Serialize to JSON array
    canonical_string = json.dumps(components, separators=(',', ':'))
    return hashlib.sha256(canonical_string.encode('utf-8')).hexdigest()
