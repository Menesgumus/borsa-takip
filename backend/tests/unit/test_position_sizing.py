from decimal import Decimal
import pytest
from app.services.position_sizing import calculate_position_sizing
from app.db.models import DecisionAction

def test_position_sizing_no_cash():
    res = calculate_position_sizing(
        available_cash=Decimal("0"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=0,
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.BUY,
        data_state="LIVE",
        risk_tolerance="MEDIUM"
    )
    assert res.sizing_state == "NO_CASH"
    assert res.recommended_budget == Decimal("0")
    assert res.recommended_quantity == 0

def test_position_sizing_low_risk_buy():
    res = calculate_position_sizing(
        available_cash=Decimal("10000"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=0,
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.BUY,
        data_state="LIVE",
        risk_tolerance="LOW"
    )
    # Target 7.5% -> 750
    assert res.sizing_state == "OK"
    assert res.recommended_budget == Decimal("700") # floored to 7 shares * 100
    assert res.recommended_quantity == 7

def test_position_sizing_medium_risk_buy():
    res = calculate_position_sizing(
        available_cash=Decimal("10000"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=0,
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.BUY,
        data_state="LIVE",
        risk_tolerance="MEDIUM"
    )
    # Target 10% -> 1000
    assert res.sizing_state == "OK"
    assert res.recommended_budget == Decimal("1000")
    assert res.recommended_quantity == 10

def test_position_sizing_high_risk_buy():
    res = calculate_position_sizing(
        available_cash=Decimal("10000"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=0,
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.BUY,
        data_state="LIVE",
        risk_tolerance="HIGH"
    )
    # Target 15% -> 1500
    assert res.sizing_state == "OK"
    assert res.recommended_budget == Decimal("1500")
    assert res.recommended_quantity == 15

def test_position_sizing_low_risk_strong_buy():
    res = calculate_position_sizing(
        available_cash=Decimal("10000"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=0,
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.STRONG_BUY,
        data_state="LIVE",
        risk_tolerance="LOW"
    )
    # Target 10% -> 1000
    assert res.sizing_state == "OK"
    assert res.recommended_budget == Decimal("1000")
    assert res.recommended_quantity == 10

def test_position_sizing_medium_risk_strong_buy():
    res = calculate_position_sizing(
        available_cash=Decimal("10000"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=0,
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.STRONG_BUY,
        data_state="LIVE",
        risk_tolerance="MEDIUM"
    )
    # Target 15% -> 1500
    assert res.sizing_state == "OK"
    assert res.recommended_budget == Decimal("1500")
    assert res.recommended_quantity == 15

def test_position_sizing_high_risk_strong_buy():
    res = calculate_position_sizing(
        available_cash=Decimal("10000"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=0,
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.STRONG_BUY,
        data_state="LIVE",
        risk_tolerance="HIGH"
    )
    # Target 20% -> 2000
    assert res.sizing_state == "OK"
    assert res.recommended_budget == Decimal("2000")
    assert res.recommended_quantity == 20

def test_position_sizing_existing_position():
    res = calculate_position_sizing(
        available_cash=Decimal("10000"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=5, # 500 value
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.BUY,
        data_state="LIVE",
        risk_tolerance="MEDIUM"
    )
    # Target 10% -> 1000, existing 500 -> diff 500
    assert res.sizing_state == "OK"
    assert res.recommended_budget == Decimal("500")
    assert res.recommended_quantity == 5
    assert res.estimated_post_trade_weight == Decimal("10.0")

def test_position_sizing_near_target():
    res = calculate_position_sizing(
        available_cash=Decimal("10000"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=9, # 900 value
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.BUY,
        data_state="LIVE",
        risk_tolerance="MEDIUM"
    )
    # Target 10% -> 1000, existing 900 -> diff 100 (1 share)
    assert res.sizing_state == "OK"
    assert res.recommended_budget == Decimal("100")
    assert res.recommended_quantity == 1
    assert res.estimated_post_trade_weight == Decimal("10.0")

def test_position_sizing_at_target():
    res = calculate_position_sizing(
        available_cash=Decimal("10000"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=10, # 1000 value
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.BUY,
        data_state="LIVE",
        risk_tolerance="MEDIUM"
    )
    # Target 10% -> 1000, existing 1000 -> diff 0
    assert res.sizing_state == "NOT_ACTIONABLE"
    assert res.recommended_quantity == 0

def test_position_sizing_above_target_below_hard_max():
    res = calculate_position_sizing(
        available_cash=Decimal("10000"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=12, # 1200 value (12%)
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.BUY,
        data_state="LIVE",
        risk_tolerance="MEDIUM"
    )
    # Target 10%, already at 12%, diff < 0
    assert res.sizing_state == "NOT_ACTIONABLE"
    assert res.recommended_quantity == 0

def test_position_sizing_at_hard_max():
    res = calculate_position_sizing(
        available_cash=Decimal("10000"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=30, # 3000 value (30%)
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.BUY,
        data_state="LIVE",
        risk_tolerance="HIGH"
    )
    # Target 20%, already 30%
    assert res.sizing_state == "OVER_LIMIT"
    assert res.recommended_quantity == 0

def test_position_sizing_above_hard_max():
    res = calculate_position_sizing(
        available_cash=Decimal("10000"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=35, # 35%
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.BUY,
        data_state="LIVE",
        risk_tolerance="HIGH"
    )
    assert res.sizing_state == "OVER_LIMIT"
    assert res.recommended_quantity == 0

def test_position_sizing_quantity_floor():
    res = calculate_position_sizing(
        available_cash=Decimal("50"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=0,
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.BUY,
        data_state="LIVE",
        risk_tolerance="MEDIUM"
    )
    assert res.sizing_state == "NO_CASH"
    assert res.recommended_quantity == 0

def test_position_sizing_hard_capacity():
    res = calculate_position_sizing(
        available_cash=Decimal("10000"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=25, # 2500 value (25%)
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.STRONG_BUY,
        data_state="LIVE",
        risk_tolerance="HIGH",
        hard_limit=Decimal("0.30")
    )
    # Target 20%, existing 25%. Diff < 0
    assert res.sizing_state == "NOT_ACTIONABLE"
    assert res.recommended_quantity == 0

def test_position_sizing_hard_capacity_blocks_buy():
    # Target is higher than hard_capacity somehow? No, target <= 20%, hard_limit = 30%.
    # But let's say target is 2000 (20%), existing is 0. Cash is 5000.
    # Max hard capacity = 3000 (30%).
    # Target = 2000, so we recommend 2000.
    res = calculate_position_sizing(
        available_cash=Decimal("5000"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=0, 
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.STRONG_BUY,
        data_state="LIVE",
        risk_tolerance="HIGH",
        hard_limit=Decimal("0.30")
    )
    assert res.recommended_quantity == 20

def test_position_sizing_delayed_data_metadata():
    res = calculate_position_sizing(
        available_cash=Decimal("10000"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=0,
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.BUY,
        data_state="DELAYED",
        risk_tolerance="MEDIUM"
    )
    assert res.sizing_state == "OK"
    assert "DELAYED_MARKET_DATA" in res.reason_codes
