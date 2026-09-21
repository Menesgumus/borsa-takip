from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.db.session import get_db_session
from app.db.models import PositionLifecycle
from app.core.config import settings

router = APIRouter()

class LifecycleOverrideRequest(BaseModel):
    portfolio_id: int
    instrument_id: int
    health_state: str
    recommended_action: str
    negative_confirmation_count: int = 0
    strong_sell_confirmation_count: int = 0
    recovery_confirmation_count: int = 0
    add_confirmation_count: int = 0
    data_state: str = "LIVE"
    suggested_reduce_quantity: Optional[str] = None
    suggested_remaining_quantity: Optional[str] = None
    estimated_released_cash_base: Optional[str] = None
    reason_codes: list[str] = []

@router.post("/lifecycle-override")
async def override_lifecycle(
    req: LifecycleOverrideRequest,
    db: AsyncSession = Depends(get_db_session)
):
    if settings.ENVIRONMENT != "test":
        raise HTTPException(status_code=403, detail="Only available in test environment")

    from sqlalchemy import select
    import json
    
    stmt = select(PositionLifecycle).where(
        PositionLifecycle.portfolio_id == req.portfolio_id,
        PositionLifecycle.instrument_id == req.instrument_id
    )
    result = await db.execute(stmt)
    lc = result.scalar_one_or_none()
    
    if not lc:
        lc = PositionLifecycle(
            portfolio_id=req.portfolio_id,
            instrument_id=req.instrument_id,
            episode_number=1,
            policy_version="1.0"
        )
        db.add(lc)
    
    lc.health_state = req.health_state
    lc.recommended_action = req.recommended_action
    lc.negative_confirmation_count = req.negative_confirmation_count
    lc.strong_sell_confirmation_count = req.strong_sell_confirmation_count
    lc.recovery_confirmation_count = req.recovery_confirmation_count
    lc.add_confirmation_count = req.add_confirmation_count
    lc.data_state = req.data_state
    
    from decimal import Decimal
    if req.suggested_reduce_quantity is not None:
        lc.suggested_reduce_quantity = Decimal(req.suggested_reduce_quantity)
    if req.suggested_remaining_quantity is not None:
        lc.suggested_remaining_quantity = Decimal(req.suggested_remaining_quantity)
    if req.estimated_released_cash_base is not None:
        lc.estimated_released_cash_base = Decimal(req.estimated_released_cash_base)
        
    lc.evidence = {"reason_codes": req.reason_codes, "market_view": "MOCK"}
    
    await db.commit()
    return {"status": "ok"}
