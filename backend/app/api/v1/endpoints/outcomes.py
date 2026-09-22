
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import DecisionOutcome, StrategyVersion, User
from app.db.session import get_db_session

router = APIRouter()

class StrategyVersionRead(BaseModel):
    id: int
    name: str
    version: str
    status: str
    promotion_reason: str | None

@router.get("/strategy-versions", response_model=list[StrategyVersionRead])
async def get_strategy_versions(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    res = await db.execute(select(StrategyVersion).order_by(StrategyVersion.created_at.desc()))
    return res.scalars().all()

class OutcomeRead(BaseModel):
    id: int
    decision_id: int
    return_t1: float | None
    return_t5: float | None
    return_t20: float | None
    return_t60: float | None

@router.get("/recent", response_model=list[OutcomeRead])
async def get_recent_outcomes(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    res = await db.execute(select(DecisionOutcome).where(DecisionOutcome.status != "UNTRUSTED_LEGACY_OUTCOME").order_by(DecisionOutcome.evaluated_at.desc()).limit(50))
    return res.scalars().all()

