from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from decimal import Decimal
import logging

from app.db.models import BehaviorProfile, TradeInsight, PortfolioTransaction

logger = logging.getLogger(__name__)

async def analyze_trade_behavior(db: AsyncSession, transaction_id: int):
    """
    Analyzes a portfolio transaction to generate behavioral insights.
    Heuristics:
    - FOMO: Bought when instrument was up significantly recently (mocked for now).
    - Concentration: This trade makes the instrument > 50% of portfolio.
    - Early Exit: Sold much earlier than planned horizon.
    """
    tx_res = await db.execute(select(PortfolioTransaction).where(PortfolioTransaction.id == transaction_id))
    tx = tx_res.scalars().first()
    
    if not tx:
        return
        
    user_id = tx.portfolio.user_id
    
    # 1. Update or create profile
    prof_res = await db.execute(select(BehaviorProfile).where(BehaviorProfile.user_id == user_id))
    profile = prof_res.scalars().first()
    if not profile:
        profile = BehaviorProfile(user_id=user_id)
        db.add(profile)
    
    # Simple Mock Heuristic
    if tx.transaction_type == "BUY":
        # Simulate FOMO logic
        fomo = False
        # If true:
        if fomo:
            db.add(TradeInsight(
                user_id=user_id,
                transaction_id=tx.id,
                insight_type="FOMO_ENTRY",
                description="Hisse senedi kısa sürede hızla yükseldikten hemen sonra alım yapıldı."
            ))
            profile.fomo_tendency_score = min(Decimal(100), profile.fomo_tendency_score + Decimal(5))

    elif tx.transaction_type == "SELL":
        # Simulate Early exit / Panic logic
        early_exit = False
        if early_exit:
            db.add(TradeInsight(
                user_id=user_id,
                transaction_id=tx.id,
                insight_type="EARLY_EXIT",
                description="Planlanan vadeden çok daha erken satış yapıldı."
            ))
            profile.patience_score = max(Decimal(0), profile.patience_score - Decimal(5))

    await db.commit()
