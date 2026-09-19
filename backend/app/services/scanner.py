import json
import logging
import time
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.redis import redis_client
from app.db.models import FundamentalData, Instrument, Portfolio, User, UserProfile, AssetClass
from app.market.exceptions import ProviderUnavailableError
from app.market.registry import registry
from app.schemas.decision import (
    FundamentalInputs,
    Horizon,
    NewsInputs,
    PortfolioFitInputs,
    TechnicalInputs,
)
from app.schemas.opportunity import OpportunityResult, PositionSizingResult
from app.services.decision_engine import evaluate_decision
from app.services.portfolio_valuation import evaluate_portfolios
from app.services.position_sizing import calculate_position_sizing
from app.services.provider_resolver import resolve_provider
from app.services.scanner_technical import get_batched_technical_inputs

logger = logging.getLogger(__name__)

async def scan_opportunities(db: AsyncSession, user: User, portfolio_id: int | None = None, limit: int = 10, symbols: list[str] | None = None) -> list[OpportunityResult]:
    t0 = time.perf_counter()
    # 1. Fetch user profile
    p_res = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = p_res.scalars().first()
    risk_tolerance = profile.risk_tolerance.value if profile and profile.risk_tolerance else "MEDIUM"

    # 2. Portfolio Valuation
    portfolio = None
    portfolio_valuation = None
    if portfolio_id:
        port_res = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
        portfolio = port_res.scalars().first()
        if portfolio:
            valuations = await evaluate_portfolios(db, [portfolio])
            portfolio_valuation = valuations.get(portfolio.id)

    # Cache Keys

    from app.services.decision_engine import ENGINE_VERSION
    redis = redis_client
    cache_key = f"opportunities:market:v5:{risk_tolerance}:{ENGINE_VERSION}" # Global market cache key

    market_results: dict[str, dict] = {}

    if redis:
        cached = await redis.get(cache_key)
        if cached:
            try:
                market_results = json.loads(cached)
            except Exception:
                market_results = {}

    if not market_results:
        stmt = select(Instrument).options(selectinload(Instrument.provider_mappings)).where(
            Instrument.is_active == True,
            Instrument.asset_class != AssetClass.FX_REFERENCE
        )
        if symbols:
            stmt = stmt.where(Instrument.symbol.in_(symbols))

        i_res = await db.execute(stmt)
        instruments = i_res.scalars().all()
        inst_ids = [inst.id for inst in instruments]

        if not instruments:
            return []

        f_res = await db.execute(
            select(FundamentalData)
            .where(FundamentalData.instrument_id.in_(inst_ids))
            .order_by(FundamentalData.instrument_id, FundamentalData.id.desc())
        )
        fundamentals = {}
        for f in f_res.scalars().all():
            if f.instrument_id not in fundamentals:
                fundamentals[f.instrument_id] = f

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

        all_symbols = [inst.symbol for inst in instruments]
        tech_map = await get_batched_technical_inputs(db, all_symbols)

        for inst in instruments:
            quote = quotes.get(inst.id)

            tech = tech_map.get(inst.symbol) or TechnicalInputs()
            if quote and quote.price is not None:
                tech.current_price = Decimal(str(quote.price))
                tech.is_stale = (quote.data_state not in ("LIVE", "DELAYED"))

            fund = FundamentalInputs(instrument_type=inst.instrument_type.value)
            f_db = fundamentals.get(inst.id)
            if f_db:
                if f_db.pe_ratio: fund.pe_ratio = Decimal(str(f_db.pe_ratio))
                if f_db.pb_ratio: fund.pb_ratio = Decimal(str(f_db.pb_ratio))

            news = NewsInputs(sentiment_score=None, is_mock=False, news_count=0)

            decision = evaluate_decision(inst.id, Horizon.MEDIUM, tech, fund, news, None)

            market_results[str(inst.id)] = {
                "instrument_id": inst.id,
                "symbol": inst.symbol,
                "name": inst.name,
                "quote_price": str(quote.price) if quote and quote.price else None,
                "quote_data_state": quote.data_state if quote else None,
                "quote_as_of": quote.timestamp.isoformat() if quote else None,

                "market_score": str(decision.overall_market_score),
                "data_quality_score": str(decision.data_quality_score),
                "technical_score": str(decision.technical_score) if decision.technical_score else None,
                "fundamental_score": str(decision.fundamental_score) if decision.fundamental_score else None,
                "news_score": str(decision.news_score) if decision.news_score else None,
                "risk_reward_score": str(decision.risk_reward_score) if decision.risk_reward_score else None,

                "market_view": decision.market_view.value,
                "reason_codes": decision.reason_codes,
                "warnings": decision.warnings,
                "missing_data": decision.missing_data,
                "decision_state": decision.decision_state,
                "engine_version": decision.engine_version,
            }

        if symbols is None and redis:
            await redis.set(cache_key, json.dumps(market_results), ex=60)

    final_results = []

    inst_res = await db.execute(select(Instrument).where(Instrument.id.in_([int(k) for k in market_results.keys()])))
    inst_dict = {inst.id: inst for inst in inst_res.scalars().all()}

    for str_id, mr in market_results.items():
        inst_id = int(str_id)
        if symbols and mr["symbol"] not in symbols:
            continue

        inst = inst_dict.get(inst_id)
        if not inst:
            continue

        quote_price_val = Decimal(mr["quote_price"]) if mr["quote_price"] else None

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

        import app.schemas.decision as dec

        market_view_enum = dec.DecisionAction(mr["market_view"])
        personal_action = None
        portfolio_fit_score = None

        if p_fit is None:
            personal_action = market_view_enum
        else:
            target_alloc = p_fit.max_weight_limit
            capacity = target_alloc - p_fit.current_weight

            if capacity >= Decimal("5"):
                portfolio_fit_score = Decimal("100")
            elif capacity > Decimal("0"):
                portfolio_fit_score = Decimal("50")
            else:
                portfolio_fit_score = Decimal("0")

            personal_action = market_view_enum

            if portfolio_fit_score < Decimal("30"):
                if personal_action in (dec.DecisionAction.STRONG_BUY, dec.DecisionAction.BUY):
                    personal_action = dec.DecisionAction.HOLD

        sizing = None
        if portfolio and portfolio_valuation and quote_price_val is not None and not mr["missing_data"]:
            if not portfolio_valuation.valuation_complete:
                personal_action = None
                sizing = PositionSizingResult(
                    available_cash=portfolio_valuation.cash_balance,
                    current_price=quote_price_val,
                    current_quantity=current_quantity,
                    current_position_value=current_position_value if current_position_value is not None else Decimal("0"),
                    current_weight_percentage=None,
                    recommended_quantity=0,
                    recommended_budget=None,
                    recommended_target_weight=None,
                    max_executable_quantity=0,
                    max_executable_budget=None,
                    theoretical_max_additional_budget=None,
                    hard_max_weight=Decimal("30"),
                    estimated_post_trade_weight=None,
                    sizing_state="VALUATION_INCOMPLETE",
                    reason_codes=["PORTFOLIO_VALUATION_INCOMPLETE"],
                    data_state=mr["quote_data_state"],
                    calculated_at=datetime.now(UTC)
                )
            else:
                sizing = calculate_position_sizing(
                    available_cash=portfolio_valuation.cash_balance,
                    total_portfolio_value=portfolio_valuation.total_market_value,
                    current_price=quote_price_val,
                    current_quantity=current_quantity,
                    market_view=market_view_enum,
                    personal_action=personal_action,
                    data_state=mr["quote_data_state"],
                    hard_limit=Decimal("0.30"),
                    risk_tolerance=risk_tolerance
                )

        def parse_dec(val: str | None) -> Decimal | None:
            return Decimal(val) if val else None

        res = OpportunityResult(
            instrument_id=inst.id,
            symbol=inst.symbol,
            name=inst.name,
            asset_class=str(inst.asset_class),
            currency=inst.currency,
            quote_price=quote_price_val,
            quote_data_state=mr["quote_data_state"],
            quote_as_of=datetime.fromisoformat(mr["quote_as_of"]) if mr["quote_as_of"] else None,

            market_score=parse_dec(mr["market_score"]),
            personal_score=None,
            portfolio_fit_score=portfolio_fit_score,
            data_quality_score=parse_dec(mr["data_quality_score"]),

            technical_score=parse_dec(mr["technical_score"]),
            fundamental_score=parse_dec(mr["fundamental_score"]),
            news_score=parse_dec(mr["news_score"]),
            risk_reward_score=parse_dec(mr["risk_reward_score"]),

            market_view=mr["market_view"],
            personal_action=personal_action.value if personal_action else None,

            reason_codes=mr["reason_codes"],
            warnings=mr["warnings"],

            missing_data=mr["missing_data"],
            decision_state=mr["decision_state"],
            calculated_at=datetime.now(UTC),
            engine_version=mr["engine_version"],

            selected_portfolio_id=portfolio.id if portfolio else None,

            current_position_quantity=current_quantity if portfolio else None,
            current_position_market_value=current_position_value if portfolio else None,
            current_position_weight_percentage=sizing.current_weight_percentage if sizing else None,

            recommended_budget=sizing.recommended_budget if sizing else None,
            recommended_quantity=sizing.recommended_quantity if sizing else None,
            recommended_target_weight=sizing.recommended_target_weight if sizing else None,

            max_executable_quantity=sizing.max_executable_quantity if sizing else None,
            max_executable_budget=sizing.max_executable_budget if sizing else None,
            theoretical_max_additional_budget=sizing.theoretical_max_additional_budget if sizing else None,

            hard_max_weight=sizing.hard_max_weight if sizing else None,
            estimated_post_trade_weight=sizing.estimated_post_trade_weight if sizing else None,

            sizing_state=sizing.sizing_state if sizing else None,
            sizing_reason_codes=sizing.reason_codes if sizing else []
        )
        final_results.append(res)

    final_results.sort(key=lambda x: (
        x.missing_data,
        -(x.market_score or Decimal("0")),
        x.symbol
    ))
    if limit > 0:
        final_results = final_results[:limit]

    t1 = time.perf_counter()
    logger.info(f"Scanner generated {len(final_results)} opportunities in {t1 - t0:.4f}s")

    return final_results
