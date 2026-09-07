from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import BehaviorProfile, TradeInsight, User
from app.db.session import get_db_session

router = APIRouter()

class ProfileRead(BaseModel):
    user_id: int
    fomo_tendency_score: Decimal
    patience_score: Decimal
    concentration_risk: Decimal

class InsightRead(BaseModel):
    id: int
    transaction_id: int
    insight_type: str
    description: str

@router.get("/profile", response_model=ProfileRead)
async def get_my_behavior_profile(db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    res = await db.execute(select(BehaviorProfile).where(BehaviorProfile.user_id == current_user.id))
    profile = res.scalars().first()
    if not profile:
        profile = BehaviorProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile

@router.get("/insights", response_model=list[InsightRead])
async def get_my_insights(db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    res = await db.execute(select(TradeInsight).where(TradeInsight.user_id == current_user.id).order_by(TradeInsight.created_at.desc()).limit(20))
    return res.scalars().all()
