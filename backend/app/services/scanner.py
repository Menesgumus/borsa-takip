from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.models import FundamentalData, Instrument, Portfolio, User, UserProfile
from app.market.exceptions import ProviderUnavailableError
from app.market.registry import registry
from app.schemas.decision import (
    FundamentalInputs,
    Horizon,
    NewsInputs,
    PortfolioFitInputs,
    TechnicalInputs,
)
from app.schemas.opportunity import OpportunityResult
from app.services.decision_engine import evaluate_decision
from app.services.portfolio_valuation import evaluate_portfolios
from app.services.position_sizing import calculate_position_sizing
from app.services.provider_resolver import resolve_provider
from app.services.technical_data import get_technical_analysis


async def scan_opportunities(db: AsyncSession, user: User, portfolio_id: int | None = None, limit: int = 10, symbols: list[str] | None = None) -> list[OpportunityResult]:
    # 1. Fetch all active instruments (or specific ones)
    stmt = select(Instrument).options(selectinload(Instrument.provider_mappings)).where(Instrument.is_active == True)
    if symbols:
        stmt = stmt.where(Instrument.symbol.in_(symbols))

    i_res = await db.execute(stmt)
    instruments = i_res.scalars().all()
    inst_ids = [inst.id for inst in instruments]

    if not instruments:
        return []

    # Fetch user profile
    p_res = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = p_res.scalars().first()
    risk_tolerance = profile.risk_tolerance.value if profile and profile.risk_tolerance else "MEDIUM"

    # 2. Portfolio Valuation
    portfolio = None
    portfolio_valuation = None
    if portfolio_id:
        # Assumes IDOR check is done in endpoint
        port_res = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
        portfolio = port_res.scalars().first()
        if portfolio:
            valuations = await evaluate_portfolios(db, [portfolio])
            portfolio_valuation = valuations.get(portfolio.id)

    # 3. Bulk fetch fundamentals
    f_res = await db.execute(
        select(FundamentalData)
        .where(FundamentalData.instrument_id.in_(inst_ids))
        .order_by(FundamentalData.instrument_id, FundamentalData.id.desc())
    )
    fundamentals = {}
    for f in f_res.scalars().all():
        if f.instrument_id not in fundamentals:
            fundamentals[f.instrument_id] = f

    # 4. Batch Provider Quotes
    provider_symbols = {}
    symbol_to_inst = {}
    for inst in instruments:
        try:
            resolved = resolve_provider(inst)
            provider_symbols.setdefault(resolved.provider_name, []).append(resolved.provider_symbol)
            symbol_to_inst[f"{resolved.provider_name}:{resolved.provider_symbol}"] = inst
        except ProviderUnavailableError:
            pass

    quotes = {}
    for provider_name, symbols_list in provider_symbols.items():
        try:
            q_res = await registry.get_quotes(provider_name, symbols_list)
            for q in q_res:
                inst = symbol_to_inst.get(f"{provider_name}:{q.symbol}")
                if inst:
                    quotes[inst.id] = q
        except ProviderUnavailableError:
            pass

    # 5. Technical Analysis (Sequential DB Fetch)
    tech_map = {}
    for inst in instruments:
        try:
            res = await get_technical_analysis(db, inst.symbol)
            tech_map[inst.symbol] = res
        except Exception:
            tech_map[inst.symbol] = None

    results: list[OpportunityResult] = []

    for inst in instruments:
        quote = quotes.get(inst.id)

        # Build Tech
        tech = TechnicalInputs()
        t_res = tech_map.get(inst.symbol)
        if t_res and t_res.indicators:
            latest = t_res.indicators[-1]
            tech.rsi_14 = Decimal(str(latest.rsi_14)) if latest.rsi_14 is not None else None
            tech.macd_line = Decimal(str(latest.macd_line)) if latest.macd_line is not None else None
            tech.macd_signal = Decimal(str(latest.macd_signal)) if latest.macd_signal is not None else None
            tech.sma_50 = Decimal(str(latest.sma_50)) if latest.sma_50 is not None else None
            tech.sma_200 = Decimal(str(latest.sma_200)) if latest.sma_200 is not None else None

        if quote and quote.price is not None:
            tech.current_price = Decimal(str(quote.price))
            tech.is_stale = (quote.data_state not in ("LIVE", "DELAYED"))

        # Build Fund
        fund = FundamentalInputs(instrument_type=inst.instrument_type.value)
        f_db = fundamentals.get(inst.id)
        if f_db:
            if f_db.pe_ratio: fund.pe_ratio = Decimal(str(f_db.pe_ratio))
            if f_db.pb_ratio: fund.pb_ratio = Decimal(str(f_db.pb_ratio))

        # Build News (No fake data)
        news = NewsInputs(sentiment_score=None, is_mock=False, news_count=0)

        # Build Portfolio Fit
        p_fit = None
        current_weight = None
        current_quantity = 0
        current_position_value = None
        if portfolio and portfolio_valuation:
            total_val = portfolio_valuation.total_market_value
            for pos in portfolio_valuation.positions:
                if pos["instrument_id"] == inst.id:
                    current_quantity = pos["quantity"]
                    current_position_value = pos["market_value"]
                    if portfolio_valuation.valuation_complete and total_val and total_val > 0 and current_position_value is not None:
                        current_weight = (current_position_value / total_val) * Decimal("100")
                    break

            if portfolio_valuation.valuation_complete:
                p_fit = PortfolioFitInputs(current_weight=current_weight or Decimal("0"), max_weight_limit=Decimal("30"))

        decision = evaluate_decision(inst.id, Horizon.MEDIUM, tech, fund, news, p_fit)

        # Build Sizing
        sizing = None
        if portfolio and portfolio_valuation and quote and quote.price is not None and not decision.missing_data:
            if not portfolio_valuation.valuation_complete:

                from app.schemas.opportunity import PositionSizingResult
                sizing = PositionSizingResult(
                    available_cash=portfolio_valuation.cash_balance,
                    current_price=Decimal(str(quote.price)),
                    current_quantity=current_quantity,
                    current_position_value=current_position_value if current_position_value is not None else Decimal("0"),
                    current_weight_percentage=None,
                    recommended_quantity=0,
                    recommended_budget=None,
                    recommended_target_weight=None,
                    max_additional_quantity=0,
                    max_additional_budget=None,
                    hard_max_weight=Decimal("30"),
                    estimated_post_trade_weight=None,
                    sizing_state="VALUATION_INCOMPLETE",
                    reason_codes=["PORTFOLIO_VALUATION_INCOMPLETE"],
                    data_state=quote.data_state,
                    calculated_at=datetime.now(UTC)
                )
            else:
                sizing = calculate_position_sizing(
                    available_cash=portfolio_valuation.cash_balance,
                    total_portfolio_value=portfolio_valuation.total_market_value,
                    current_price=Decimal(str(quote.price)),
                    current_quantity=current_quantity,
                    market_view=decision.market_view,
                    personal_action=decision.personal_action,
                    data_state=quote.data_state,
                    hard_limit=Decimal("0.30"),
                    risk_tolerance=risk_tolerance
                )

        res = OpportunityResult(
            instrument_id=inst.id,
            symbol=inst.symbol,
            name=inst.name,
            quote_price=Decimal(str(quote.price)) if quote and quote.price else None,
            quote_data_state=quote.data_state if quote else None,
            quote_as_of=quote.timestamp if quote else None,

            market_score=decision.overall_market_score,
            personal_score=decision.overall_personal_score,
            data_quality_score=decision.data_quality_score,

            technical_score=decision.technical_score,
            fundamental_score=decision.fundamental_score,
            news_score=decision.news_score,
            risk_reward_score=decision.risk_reward_score,

            market_view=decision.market_view.value,
            personal_action=decision.personal_action.value if decision.personal_action else None,

            reason_codes=decision.reason_codes,
            warnings=decision.warnings,

            missing_data=decision.missing_data,
            decision_state=decision.decision_state,
            calculated_at=datetime.now(UTC),
            engine_version=decision.engine_version,

            selected_portfolio_id=portfolio.id if portfolio else None,

            current_position_quantity=current_quantity if portfolio else None,
            current_position_market_value=current_position_value if portfolio else None,
            current_position_weight_percentage=sizing.current_weight_percentage if sizing else None,

            recommended_budget=sizing.recommended_budget if sizing else None,
            recommended_quantity=sizing.recommended_quantity if sizing else None,
            recommended_target_weight=sizing.recommended_target_weight if sizing else None,

            max_additional_budget=sizing.max_additional_budget if sizing else None,
            max_additional_quantity=sizing.max_additional_quantity if sizing else None,
            hard_max_weight=sizing.hard_max_weight if sizing else None,

            estimated_post_trade_weight=sizing.estimated_post_trade_weight if sizing else None,

            sizing_state=sizing.sizing_state if sizing else None,
            sizing_reason_codes=sizing.reason_codes if sizing else None
        )
        results.append(res)

    # 6. Rank: Actionable Buy first, then overall score
    def get_rank_key(r: OpportunityResult):
        # 1. Actionable personal BUY (0 for BUY, 1 for else)
        is_actionable = 1
        if r.personal_action in ["BUY", "STRONG_BUY"] and r.sizing_state == "OK" and not r.missing_data:
            is_actionable = 0

        # 2. Overall score (Personal if available, else Market)
        score = r.personal_score if r.personal_score is not None else r.market_score

        return (
            r.missing_data,
            is_actionable,
            -float(score) if score is not None else 0,
            -float(r.data_quality_score),
            r.symbol
        )

    results.sort(key=get_rank_key)

    # 7. Apply limit
    limit = max(1, min(limit, 100))
    return results[:limit]
