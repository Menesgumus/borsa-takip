from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import Portfolio, User
from app.db.session import get_db_session
from app.schemas.opportunity import OpportunityResult
from app.services.scanner import scan_opportunities

router = APIRouter()

@router.get("", response_model=list[OpportunityResult])
async def get_opportunities(
    portfolio_id: int | None = Query(None),
    asset_class: str | None = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    if portfolio_id:
        # IDOR protection
        p_res = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id))
        if not p_res.scalars().first():
            raise HTTPException(status_code=404, detail="Portfolio not found or unauthorized")

    results = await scan_opportunities(db, user=current_user, portfolio_id=portfolio_id, limit=limit)
    if asset_class and asset_class != "ALL":
        results = [r for r in results if r.asset_class == asset_class]
    return results

@router.get('/{symbol}', response_model=OpportunityResult)
async def get_opportunity_detail(
    symbol: str,
    portfolio_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    if portfolio_id:
        p_res = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id))
        if not p_res.scalars().first():
            raise HTTPException(status_code=404, detail="Portfolio not found or unauthorized")

    results = await scan_opportunities(db, user=current_user, portfolio_id=portfolio_id, limit=1, symbols=[symbol.upper()])
    if not results:
        raise HTTPException(status_code=404, detail="Instrument not found or not active")
    return results[0]

