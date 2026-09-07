from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db.session import get_db_session
from app.db.models import DecisionOutcome, StrategyVersion
from pydantic import BaseModel

router = APIRouter()

class StrategyVersionRead(BaseModel):
    id: int
    name: str
    version: str
    status: str
    promotion_reason: str | None

@router.get("/strategy-versions", response_model=List[StrategyVersionRead])
async def get_strategy_versions(db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(StrategyVersion).order_by(StrategyVersion.created_at.desc()))
    return res.scalars().all()

class OutcomeRead(BaseModel):
    id: int
    decision_id: int
    return_t1: float | None
    return_t5: float | None
    return_t20: float | None
    return_t60: float | None

@router.get("/recent", response_model=List[OutcomeRead])
async def get_recent_outcomes(db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(DecisionOutcome).order_by(DecisionOutcome.evaluated_at.desc()).limit(50))
    return res.scalars().all()

@router.post("/trigger-tracker")
async def trigger_tracker_worker(db: AsyncSession = Depends(get_db_session)):
    from app.services.outcome_tracker import track_outcomes, evaluate_strategy_versions
    await track_outcomes(db)
    await evaluate_strategy_versions(db)
    return {"status": "success"}
