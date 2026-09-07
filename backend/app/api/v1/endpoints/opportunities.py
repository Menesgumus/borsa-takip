
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import Portfolio, User
from app.db.session import get_db_session
from app.schemas.scanner import OpportunityResult
from app.services.scanner import scan_opportunities

router = APIRouter()

@router.get("/", response_model=list[OpportunityResult])
async def get_opportunities(
    portfolio_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    if portfolio_id:
        # IDOR protection
        p_res = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id))
        if not p_res.scalars().first():
            raise HTTPException(status_code=404, detail="Portfolio not found or unauthorized")

    results = await scan_opportunities(db, portfolio_id=portfolio_id)
    return results
