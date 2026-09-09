import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import FundamentalData, Instrument, Portfolio
from app.schemas.decision import (
    FundamentalInputs,
    Horizon,
    NewsInputs,
    PortfolioFitInputs,
    TechnicalInputs,
)
from app.schemas.scanner import OpportunityResult
from app.services.decision_engine import evaluate_decision


async def scan_opportunities(db: AsyncSession, portfolio_id: int | None = None) -> list[OpportunityResult]:
    # 1. Fetch all active instruments
    i_res = await db.execute(select(Instrument).where(Instrument.is_active == True))
    instruments = i_res.scalars().all()
    inst_ids = [inst.id for inst in instruments]

    portfolio = None
    if portfolio_id:
        p_res = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
        portfolio = p_res.scalars().first()

    # Bulk fetch fundamentals (latest per instrument) to avoid N+1
    f_res = await db.execute(
        select(FundamentalData)
        .where(FundamentalData.instrument_id.in_(inst_ids))
        .order_by(FundamentalData.instrument_id, FundamentalData.id.desc())
    )
    fundamentals = {}
    for f in f_res.scalars().all():
        if f.instrument_id not in fundamentals:
            fundamentals[f.instrument_id] = f

    results = []

    for inst in instruments:
        # Evaluate Decision Engine per instrument (Phase 10 reuse)

        # Provide Mock empty records to test evaluation logic, or pull from DB.
        # This mirrors the Phase 10 integration tests which pass empty dicts if missing

        tech = TechnicalInputs()
        fund = FundamentalInputs()
        news = NewsInputs()

        f_db = fundamentals.get(inst.id)
        if f_db:
            if f_db.pe_ratio: fund.pe_ratio = f_db.pe_ratio
            if f_db.pb_ratio: fund.pb_ratio = f_db.pb_ratio

        p_fit = None
        if portfolio:
            p_fit = PortfolioFitInputs()

        decision = evaluate_decision(inst.id, Horizon.MEDIUM, tech, fund, news, p_fit)


        res = OpportunityResult(
            instrument_symbol=inst.symbol,
            instrument_name=inst.name,
            raw_score=decision.overall_market_score,
            market_view=decision.market_view.value,
            user_fit_score=decision.portfolio_fit_score,
            personal_action=decision.personal_action.value if decision.personal_action else None,
            reasons=decision.reason_codes,
            warnings=decision.warnings,
            missing_data=decision.missing_data,
            calculated_at=datetime.datetime.now(datetime.UTC),
            engine_version=decision.engine_version
        )
        results.append(res)

    # 2. Filter & Rank
    # Rule: Stale Data / Missing Data -> Suppressed / Push to bottom
    # We sort by:
    # missing_data ASC (False comes first)
    # raw_score DESC
    # symbol ASC (deterministic tie-breaking)

    results.sort(key=lambda x: (
        x.missing_data,
        -float(x.raw_score),
        x.instrument_symbol
    ))

    return results
