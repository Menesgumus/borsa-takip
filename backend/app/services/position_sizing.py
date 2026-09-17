import math
from datetime import UTC, datetime
from decimal import Decimal

from app.db.models import DecisionAction
from app.schemas.opportunity import PositionSizingResult


def calculate_position_sizing(
    available_cash: Decimal,
    total_portfolio_value: Decimal,
    current_price: Decimal,
    current_quantity: int,
    market_view: DecisionAction,
    personal_action: DecisionAction | None,
    data_state: str,
    hard_limit: Decimal = Decimal("0.30"),
    risk_tolerance: str = "MEDIUM"
) -> PositionSizingResult:
    """
    Given portfolio context, candidate price, and decision, calculate sizing.
    Uses target weight mapping based on risk tolerance and conviction.
    """
    if current_price <= 0:
        raise ValueError("Current price must be positive")

    current_position_value = Decimal(current_quantity) * current_price

    # Portfolio total V should theoretically include the current position value
    # V is total_portfolio_value
    if total_portfolio_value <= 0:
        current_weight_percentage = Decimal("0")
    else:
        current_weight_percentage = current_position_value / total_portfolio_value

    hard_capacity = max(Decimal("0"), hard_limit * total_portfolio_value - current_position_value)
    max_additional_budget = min(available_cash, hard_capacity)
    max_additional_quantity = math.floor(max_additional_budget / current_price)

    # Determine target weight
    # Default policy:
    # LOW: 0.075 (7.5%)
    # MEDIUM: 0.10 (10%)
    # HIGH: 0.15 (15%)
    # For STRONG_BUY:
    # LOW: 0.10
    # MEDIUM: 0.15
    # HIGH: 0.20

    target_weights = {
        "LOW": {"BUY": Decimal("0.075"), "STRONG_BUY": Decimal("0.10")},
        "MEDIUM": {"BUY": Decimal("0.10"), "STRONG_BUY": Decimal("0.15")},
        "HIGH": {"BUY": Decimal("0.15"), "STRONG_BUY": Decimal("0.20")}
    }

    # Default risk tolerance to MEDIUM if not matched
    rt = risk_tolerance if risk_tolerance in target_weights else "MEDIUM"

    # Use personal action if available, else market view
    action_str = personal_action.value if personal_action else market_view.value

    target_weight = Decimal("0")
    if action_str in ["BUY", "STRONG_BUY"]:
        target_weight = target_weights[rt].get(action_str, target_weights[rt]["BUY"])

    target_position_value = target_weight * total_portfolio_value
    desired_additional_value = max(Decimal("0"), target_position_value - current_position_value)

    recommended_budget = min(desired_additional_value, available_cash, hard_capacity)
    recommended_quantity = math.floor(recommended_budget / current_price)

    # Recalculate actual recommended budget based on integer quantity
    actual_recommended_budget = Decimal(recommended_quantity) * current_price

    post_trade_value = current_position_value + actual_recommended_budget
    if total_portfolio_value <= 0:
        estimated_post_trade_weight = Decimal("0")
    else:
        estimated_post_trade_weight = post_trade_value / total_portfolio_value

    reason_codes = []

    if data_state == "DELAYED":
        reason_codes.append("DELAYED_MARKET_DATA")

    if action_str not in ["BUY", "STRONG_BUY"]:
        sizing_state = "NOT_ACTIONABLE"
        recommended_budget = Decimal("0")
        recommended_quantity = 0
        actual_recommended_budget = Decimal("0")
        reason_codes.append("NON_BUY_ACTION")
    elif current_weight_percentage >= hard_limit:
        sizing_state = "OVER_LIMIT"
        recommended_budget = Decimal("0")
        recommended_quantity = 0
        actual_recommended_budget = Decimal("0")
        reason_codes.append("PORTFOLIO_CONCENTRATION_LIMIT")
    elif recommended_quantity < 1:
        if available_cash < current_price:
            sizing_state = "NO_CASH"
            reason_codes.append("INSUFFICIENT_CASH_FOR_ONE_SHARE")
        else:
            sizing_state = "NOT_ACTIONABLE"
            reason_codes.append("INSUFFICIENT_CAPACITY_FOR_ONE_SHARE")
    else:
        sizing_state = "OK"

    return PositionSizingResult(
        available_cash=available_cash,
        current_price=current_price,
        current_quantity=current_quantity,
        current_position_value=current_position_value,
        current_weight_percentage=current_weight_percentage * Decimal("100"),
        recommended_budget=actual_recommended_budget,
        recommended_quantity=recommended_quantity,
        recommended_target_weight=target_weight * Decimal("100"),
        max_additional_budget=max_additional_budget,
        max_additional_quantity=max_additional_quantity,
        hard_max_weight=hard_limit * Decimal("100"),
        estimated_post_trade_weight=estimated_post_trade_weight * Decimal("100"),
        sizing_state=sizing_state,
        reason_codes=reason_codes,
        data_state=data_state,
        calculated_at=datetime.now(UTC)
    )
