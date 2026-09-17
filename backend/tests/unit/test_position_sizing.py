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
        data_state="LIVE"
    )
    assert res.sizing_state == "NO_CASH"
    assert res.recommended_budget == Decimal("0")
    assert res.recommended_quantity == 0

def test_position_sizing_ok():
    res = calculate_position_sizing(
        available_cash=Decimal("5000"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=0,
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.BUY,
        data_state="LIVE"
    )
    assert res.sizing_state == "OK"
    # Target for BUY MODERATE is 10%, so 1000
    assert res.recommended_budget == Decimal("1000")
    assert res.recommended_quantity == 10
    
def test_position_sizing_over_limit():
    res = calculate_position_sizing(
        available_cash=Decimal("5000"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=35, # 3500 value, 35% weight
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.BUY,
        data_state="LIVE"
    )
    assert res.sizing_state == "OVER_LIMIT"
    assert res.recommended_quantity == 0

def test_position_sizing_near_limit():
    res = calculate_position_sizing(
        available_cash=Decimal("5000"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=28, # 2800 value, 28% weight
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.STRONG_BUY,
        data_state="LIVE"
    )
    # Target for STRONG_BUY MODERATE is 15% (1500), but we already have 2800.
    # So we want 0 additional value according to target, BUT wait.
    # The current policy is: `desired_additional = max(0, target_position_value - current_position_value)`
    # target = 1500, current = 2800, max(0, -1300) = 0.
    # Therefore it should be NOT_ACTIONABLE due to insufficient capacity for one share.
    assert res.recommended_quantity == 0
    assert res.sizing_state == "NOT_ACTIONABLE"

def test_position_sizing_quantity_floor():
    res = calculate_position_sizing(
        available_cash=Decimal("50"),
        total_portfolio_value=Decimal("10000"),
        current_price=Decimal("100"),
        current_quantity=0,
        market_view=DecisionAction.BUY,
        personal_action=DecisionAction.BUY,
        data_state="LIVE"
    )
    assert res.sizing_state == "NO_CASH"
    assert res.recommended_quantity == 0

