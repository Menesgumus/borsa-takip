import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import StrategyVersion

logger = logging.getLogger(__name__)

async def track_outcomes(db: AsyncSession):
    """
    Placeholder for future real Phase 30 historical evaluation.
    Legacy fake zeros have been quarantined.
    """
    logger.info("track_outcomes is temporarily disabled pending Phase 30 data readiness.")
    pass

async def evaluate_strategy_versions(db: AsyncSession):
    """
    Champion vs Challenger Evaluation
    NO AUTO-PROMOTION. Only marks status as BLOCKED_BY_DATA_VALIDATION if attempted.
    """
    challengers = await db.execute(select(StrategyVersion).where(StrategyVersion.status == "CHALLENGER"))

    for challenger in challengers.scalars().all():
        logger.warning(f"Challenger {challenger.version} evaluation is deferred until Phase 30 real validation.")
        challenger.promotion_reason = "BLOCKED_BY_DATA_VALIDATION"

    await db.commit()

