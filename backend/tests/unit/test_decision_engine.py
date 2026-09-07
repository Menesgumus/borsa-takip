import pytest
from decimal import Decimal
from app.schemas.decision import TechnicalInputs, FundamentalInputs
from app.services.decision_engine import evaluate_decision
from app.db.models import DecisionAction

def test_missing_data_returns_hold():
    tech = TechnicalInputs(current_price=None, rsi_14=None)
    fund = FundamentalInputs()
    res = evaluate_decision(1, tech, fund)
    assert res.action == DecisionAction.HOLD
    assert res.missing_data is True
    assert "MISSING_CRITICAL_DATA" in res.reason_codes

def test_strong_buy_golden_fixture():
    # RSI < 30 (1.0), MACD > Signal (1.0), Price > 50 > 200 (1.0), PE < 15 & PB < 2 (1.0)
    # Average = 1.0 >= 0.75 -> STRONG_BUY
    tech = TechnicalInputs(
        current_price=Decimal("150"),
        rsi_14=Decimal("25"),
        macd_line=Decimal("2.0"),
        macd_signal=Decimal("1.0"),
        sma_50=Decimal("140"),
        sma_200=Decimal("120")
    )
    fund = FundamentalInputs(pe_ratio=Decimal("10"), pb_ratio=Decimal("1.5"))
    
    res = evaluate_decision(1, tech, fund)
    assert res.score == Decimal("1.0")
    assert res.action == DecisionAction.STRONG_BUY
    assert "RSI_OVERSOLD" in res.reason_codes

def test_sell_golden_fixture():
    # RSI = 50 (0.0), MACD < Signal (-1.0), Price < 50 < 200 (-1.0), PE = 20 (0.0)
    # Average = -2.0 / 4 = -0.5 <= -0.25 -> SELL
    tech = TechnicalInputs(
        current_price=Decimal("90"),
        rsi_14=Decimal("50"),
        macd_line=Decimal("-1.0"),
        macd_signal=Decimal("-0.5"),
        sma_50=Decimal("100"),
        sma_200=Decimal("120")
    )
    fund = FundamentalInputs(pe_ratio=Decimal("20"), pb_ratio=Decimal("3.0"))
    
    res = evaluate_decision(1, tech, fund)
    assert res.score == Decimal("-0.5")
    assert res.action == DecisionAction.SELL
    assert "MACD_BEARISH" in res.reason_codes

def test_neutral_hold_golden_fixture():
    # Everything neutral (0.0)
    tech = TechnicalInputs(
        current_price=Decimal("110"),
        rsi_14=Decimal("50"),
        macd_line=Decimal("0.0"),
        macd_signal=Decimal("0.0"),
        sma_50=Decimal("110"), # wait, > needs strict inequality
        sma_200=Decimal("110")
    )
    fund = FundamentalInputs(pe_ratio=Decimal("20"), pb_ratio=Decimal("3.0"))
    
    res = evaluate_decision(1, tech, fund)
    assert res.score == Decimal("0.0")
    assert res.action == DecisionAction.HOLD
    assert "RSI_NEUTRAL" in res.reason_codes
