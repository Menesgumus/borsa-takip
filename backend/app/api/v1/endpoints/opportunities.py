from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.endpoints.auth import get_current_user
from app.core.redis import redis_client
from app.db.models import Portfolio, User
from app.db.session import get_db_session
from app.schemas.opportunity import OpportunityResult
from app.services.decision_engine import ENGINE_VERSION
from app.services.scanner import scan_opportunities

router = APIRouter()

@router.get("", response_model=list[OpportunityResult])
async def get_opportunities(
    portfolio_id: int | None = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    if portfolio_id:
        # IDOR protection
        p_res = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id))
        if not p_res.scalars().first():
            raise HTTPException(status_code=404, detail="Portfolio not found or unauthorized")

    # Cache isolation per user and portfolio
    cache_key = f"opportunities:v3:{current_user.id}:{portfolio_id or 'none'}:MEDIUM:{ENGINE_VERSION}:{limit}"

    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return Response(content=cached_data, media_type="application/json")

    results = await scan_opportunities(db, user=current_user, portfolio_id=portfolio_id, limit=limit)

    # Cache for 60 seconds due to delayed market data
    try:
        json_data = "[%s]" % ",".join([r.model_dump_json() for r in results])
        await redis_client.set(cache_key, json_data, ex=60)
    except Exception:
        pass

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

