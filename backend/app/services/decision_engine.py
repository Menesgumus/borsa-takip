from decimal import Decimal
from typing import List
from app.schemas.decision import TechnicalInputs, FundamentalInputs, DecisionResult
from app.db.models import DecisionAction

ENGINE_VERSION = "v1.0"

def evaluate_decision(
    instrument_id: int,
    tech: TechnicalInputs,
    fund: FundamentalInputs
) -> DecisionResult:
    
    # 1. Data Quality Gate
    if tech.current_price is None or tech.rsi_14 is None:
        return DecisionResult(
            instrument_id=instrument_id,
            action=DecisionAction.HOLD,
            score=Decimal("0"),
            reason_codes=["MISSING_CRITICAL_DATA"],
            missing_data=True,
            engine_version=ENGINE_VERSION
        )
        
    score_components = []
    reason_codes = []
    
    # 2. RSI Logic
    if tech.rsi_14 < Decimal("30"):
        score_components.append(Decimal("1.0"))
        reason_codes.append("RSI_OVERSOLD")
    elif tech.rsi_14 > Decimal("70"):
        score_components.append(Decimal("-1.0"))
        reason_codes.append("RSI_OVERBOUGHT")
    else:
        score_components.append(Decimal("0.0"))
        reason_codes.append("RSI_NEUTRAL")
        
    # 3. MACD Logic
    if tech.macd_line is not None and tech.macd_signal is not None:
        if tech.macd_line > tech.macd_signal:
            score_components.append(Decimal("1.0"))
            reason_codes.append("MACD_BULLISH")
        elif tech.macd_line < tech.macd_signal:
            score_components.append(Decimal("-1.0"))
            reason_codes.append("MACD_BEARISH")
        else:
            score_components.append(Decimal("0.0"))
            
    # 4. SMA Trend Logic
    if tech.sma_50 is not None and tech.sma_200 is not None:
        if tech.current_price > tech.sma_50 and tech.sma_50 > tech.sma_200:
            score_components.append(Decimal("1.0"))
            reason_codes.append("TREND_UP_GOLDEN")
        elif tech.current_price < tech.sma_50 and tech.sma_50 < tech.sma_200:
            score_components.append(Decimal("-1.0"))
            reason_codes.append("TREND_DOWN_DEATH")
        else:
            score_components.append(Decimal("0.0"))
            
    # 5. Fundamental Logic
    if fund.pe_ratio is not None and fund.pb_ratio is not None:
        if fund.pe_ratio > Decimal("0") and fund.pe_ratio < Decimal("15") and fund.pb_ratio < Decimal("2.0"):
            score_components.append(Decimal("1.0"))
            reason_codes.append("FUNDAMENTAL_UNDERVALUED")
        elif fund.pe_ratio > Decimal("30") or fund.pb_ratio > Decimal("5.0"):
            score_components.append(Decimal("-1.0"))
            reason_codes.append("FUNDAMENTAL_OVERVALUED")
        else:
            score_components.append(Decimal("0.0"))
            
    # 6. Aggregation
    if not score_components:
        final_score = Decimal("0.0")
    else:
        final_score = sum(score_components) / Decimal(len(score_components))
        
    # 7. Action mapping
    if final_score >= Decimal("0.75"):
        action = DecisionAction.STRONG_BUY
    elif final_score >= Decimal("0.25"):
        action = DecisionAction.BUY
    elif final_score <= Decimal("-0.75"):
        action = DecisionAction.STRONG_SELL
    elif final_score <= Decimal("-0.25"):
        action = DecisionAction.SELL
    else:
        action = DecisionAction.HOLD
        
    return DecisionResult(
        instrument_id=instrument_id,
        action=action,
        score=final_score,
        reason_codes=reason_codes,
        missing_data=False,
        engine_version=ENGINE_VERSION
    )
