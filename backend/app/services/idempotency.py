import hashlib
from typing import Any
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import IdempotencyRecord, PortfolioTransaction
from app.services.canonical import get_canonical_json

async def check_and_record_idempotency(
    db: AsyncSession,
    user_id: int,
    portfolio_id: int,
    mutation_family: str,
    idempotency_key: str,
    request_payload: dict,
) -> Any:
    # Hash the payload
    payload_str = get_canonical_json(request_payload)
    request_hash = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()

    # Query existing
    res = await db.execute(
        select(IdempotencyRecord)
        .where(
            IdempotencyRecord.user_id == user_id,
            IdempotencyRecord.portfolio_id == portfolio_id,
            IdempotencyRecord.mutation_family == mutation_family,
            IdempotencyRecord.idempotency_key == idempotency_key
        )
    )
    existing = res.scalars().first()

    if existing:
        if existing.request_hash == request_hash:
            # Same request, return the previous result payload
            if existing.response_payload and "transaction_id" in existing.response_payload:
                tx_id = existing.response_payload["transaction_id"]
                tx_res = await db.execute(select(PortfolioTransaction).where(PortfolioTransaction.id == tx_id))
                tx = tx_res.scalars().first()
                if tx:
                    return tx
            return existing.response_payload
        else:
            raise HTTPException(status_code=409, detail="Idempotency conflict: same key with different payload")

    return None

def build_idempotency_record(
    user_id: int,
    portfolio_id: int,
    mutation_family: str,
    idempotency_key: str,
    request_payload: dict,
    response_payload: dict
) -> IdempotencyRecord:
    payload_str = get_canonical_json(request_payload)
    request_hash = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
    
    return IdempotencyRecord(
        user_id=user_id,
        portfolio_id=portfolio_id,
        mutation_family=mutation_family,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
        response_payload=response_payload,
        status="COMPLETED"
    )
