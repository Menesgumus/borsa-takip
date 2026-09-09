from datetime import UTC, datetime
from decimal import Decimal

from app.db.models import DecisionAction
from app.schemas.decision import (
    DecisionResult,
    FundamentalInputs,
    Horizon,
    NewsInputs,
    PortfolioFitInputs,
    TechnicalInputs,
)

ENGINE_VERSION = "v2.0"

def clamp_score(score: Decimal) -> Decimal:
    return max(Decimal("0"), min(Decimal("100"), score))

def evaluate_decision(
    instrument_id: int,
    horizon: Horizon,
    tech: TechnicalInputs,
    fund: FundamentalInputs,
    news: NewsInputs,
    portfolio_fit: PortfolioFitInputs | None = None
) -> DecisionResult:

    reason_codes = []
    warnings = []

    # 1. Data Quality Score
    dq_score = Decimal("100")
    if tech.current_price is None or tech.current_price == Decimal("0"):
        dq_score -= Decimal("50")
        warnings.append("MISSING_CURRENT_PRICE")
    if tech.rsi_14 is None or tech.macd_line is None or tech.sma_50 is None:
        dq_score -= Decimal("30")
        warnings.append("INSUFFICIENT_TECHNICAL_HISTORY")
    if getattr(tech, 'is_stale', False):
        dq_score -= Decimal("20")
        warnings.append("STALE_MARKET_DATA")
    if getattr(news, 'is_mock', False):
        dq_score -= Decimal("10")
        warnings.append("LOW_DATA_QUALITY_MOCK_NEWS")

    dq_score = clamp_score(dq_score)

    if dq_score < Decimal("50") or tech.current_price is None or tech.current_price == Decimal("0"):
        return DecisionResult(
            instrument_id=instrument_id,
            horizon=horizon,
            as_of=datetime.now(UTC),
            data_quality_score=dq_score,
            overall_market_score=Decimal("0"),
            tech_score=Decimal("0"),
            fund_score=Decimal("0"),
            news_score=Decimal("0"),
            portfolio_fit_score=Decimal("0") if portfolio_fit else None,
            decision_state="INSUFFICIENT_DATA",
            market_view=DecisionAction.HOLD,
            personal_action=DecisionAction.HOLD if portfolio_fit else None,
            reason_codes=["INSUFFICIENT_DATA"],
            warnings=warnings,
            missing_data=True,
            engine_version="v2.0"
        )

    # 2. Technical Score
    tech_score = Decimal("50")
    if tech.rsi_14 is not None:
        if tech.rsi_14 < Decimal("30"):
            tech_score += Decimal("20")
            reason_codes.append("RSI_OVERSOLD")
        elif tech.rsi_14 > Decimal("70"):
            tech_score -= Decimal("20")
            reason_codes.append("RSI_OVERBOUGHT")

    if tech.macd_line is not None and tech.macd_signal is not None:
        if tech.macd_line > tech.macd_signal:
            tech_score += Decimal("15")
            reason_codes.append("MACD_BULLISH")
        elif tech.macd_line < tech.macd_signal:
            tech_score -= Decimal("15")
            reason_codes.append("MACD_BEARISH")

    if tech.sma_50 is not None and tech.sma_200 is not None and tech.current_price is not None:
        if tech.current_price > tech.sma_50 and tech.sma_50 > tech.sma_200:
            tech_score += Decimal("15")
            reason_codes.append("TREND_UP_GOLDEN")
        elif tech.current_price < tech.sma_50 and tech.sma_50 < tech.sma_200:
            tech_score -= Decimal("15")
            reason_codes.append("TREND_DOWN_DEATH")

    tech_score = clamp_score(tech_score)

    # 3. Fundamental Score
    fund_score = None
    if fund.instrument_type in ["STOCK", "ETF"]:
        f_score = Decimal("50")
        if fund.pe_ratio is not None:
            if Decimal("0") < fund.pe_ratio < Decimal("15"):
                f_score += Decimal("25")
            elif fund.pe_ratio > Decimal("30"):
                f_score -= Decimal("25")
        if fund.pb_ratio is not None:
            if Decimal("0") < fund.pb_ratio < Decimal("2.0"):
                f_score += Decimal("25")
            elif fund.pb_ratio > Decimal("5.0"):
                f_score -= Decimal("25")
        fund_score = clamp_score(f_score)
    else:
        warnings.append("FUNDAMENTALS_NOT_APPLICABLE")

    # 4. News Score
    news_score = None
    if news.sentiment_score is not None:
        news_score = clamp_score(news.sentiment_score)
    else:
        warnings.append("NEWS_UNAVAILABLE")

    # 5. Risk/Reward Score (stub for now)
    rr_score = Decimal("50")

    # 6. Overall Market Score
    weights = {"tech": Decimal("0.0"), "fund": Decimal("0.0"), "news": Decimal("0.0")}
    if fund_score is not None and news_score is not None:
        weights = {"tech": Decimal("0.4"), "fund": Decimal("0.4"), "news": Decimal("0.2")}
    elif fund_score is not None and news_score is None:
        weights = {"tech": Decimal("0.5"), "fund": Decimal("0.5"), "news": Decimal("0.0")}
    elif fund_score is None and news_score is not None:
        weights = {"tech": Decimal("0.6"), "fund": Decimal("0.0"), "news": Decimal("0.4")}
    else:
        weights = {"tech": Decimal("1.0"), "fund": Decimal("0.0"), "news": Decimal("0.0")}

    market_components = [
        tech_score * weights["tech"],
        (fund_score or Decimal("0")) * weights["fund"],
        (news_score or Decimal("0")) * weights["news"]
    ]
    overall_market = sum(market_components)

    # 7. Action Mapping Function
    def map_action(score: Decimal) -> DecisionAction:
        if score >= Decimal("80"): return DecisionAction.STRONG_BUY
        if score >= Decimal("60"): return DecisionAction.BUY
        if score >= Decimal("40"): return DecisionAction.HOLD
        if score >= Decimal("20"): return DecisionAction.SELL
        return DecisionAction.STRONG_SELL

    market_view = map_action(overall_market)

    # 8. Data Quality Fail-safe
    if dq_score < Decimal("50"):
        market_view = DecisionAction.HOLD
        reason_codes.append("INSUFFICIENT_DATA")

    # 9. Personal Action
    personal_action = None
    overall_personal = None
    fit_score = None

    if portfolio_fit is not None:
        # Calculate fit
        if portfolio_fit.current_weight >= portfolio_fit.max_weight_limit:
            fit_score = Decimal("0")
            warnings.append("PORTFOLIO_CONCENTRATION_LIMIT")
        else:
            ratio = portfolio_fit.current_weight / portfolio_fit.max_weight_limit
            fit_score = clamp_score(Decimal("100") - (ratio * Decimal("100")))

        # Adjust overall personal score
        overall_personal = (overall_market * Decimal("0.7")) + (fit_score * Decimal("0.3"))
        personal_action = map_action(overall_personal)

        # Guardrails for personal
        if dq_score < Decimal("50"):
            personal_action = DecisionAction.HOLD

        if fit_score < Decimal("20") and personal_action in [DecisionAction.STRONG_BUY, DecisionAction.BUY]:
            personal_action = DecisionAction.HOLD
            reason_codes.append("RISK_LIMIT_EXCEEDED")

    return DecisionResult(
        instrument_id=instrument_id,
        horizon=horizon,
        as_of=datetime.now(UTC),
        technical_score=tech_score,
        fundamental_score=fund_score,
        news_score=news_score,
        risk_reward_score=rr_score,
        portfolio_fit_score=fit_score,
        data_quality_score=dq_score,
        overall_market_score=overall_market,
        overall_personal_score=overall_personal,
        decision_state="AVAILABLE",
        market_view=market_view,
        personal_action=personal_action,
        reason_codes=reason_codes,
        warnings=warnings,
        missing_data=(dq_score < Decimal("50")),
        engine_version=ENGINE_VERSION
    )
