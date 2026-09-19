from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class PositionSizingResult(BaseModel):
    available_cash: Decimal
    current_price: Decimal
    current_quantity: int
    current_position_value: Decimal
    current_weight_percentage: Decimal | None = None

    recommended_budget: Decimal | None = None
    recommended_quantity: int
    recommended_target_weight: Decimal | None = None

    max_executable_budget: Decimal | None = None
    max_executable_quantity: int
    theoretical_max_additional_budget: Decimal | None = None
    hard_max_weight: Decimal | None = None

    estimated_post_trade_weight: Decimal | None = None

    sizing_state: Literal["OK", "OVER_LIMIT", "NO_CASH", "NOT_ACTIONABLE", "VALUATION_INCOMPLETE"]
    reason_codes: list[str]
    data_state: str
    calculated_at: datetime

class OpportunityResult(BaseModel):
    instrument_id: int
    symbol: str
    name: str
    asset_class: str
    currency: str

    quote_price: Decimal | None = None
    quote_data_state: str | None = None
    quote_as_of: datetime | None = None

    market_score: Decimal | None = None
    personal_score: Decimal | None = None
    portfolio_fit_score: Decimal | None = None
    data_quality_score: Decimal

    technical_score: Decimal | None = None
    fundamental_score: Decimal | None = None
    news_score: Decimal | None = None
    risk_reward_score: Decimal | None = None

    market_view: str
    personal_action: str | None = None

    reason_codes: list[str]
    warnings: list[str]

    missing_data: bool
    decision_state: str
    calculated_at: datetime
    engine_version: str

    selected_portfolio_id: int | None = None

    current_position_quantity: int | None = None
    current_position_market_value: Decimal | None = None
    current_position_weight_percentage: Decimal | None = None

    recommended_budget: Decimal | None = None
    recommended_quantity: int | None = None
    recommended_target_weight: Decimal | None = None

    max_executable_budget: Decimal | None = None
    max_executable_quantity: int | None = None
    theoretical_max_additional_budget: Decimal | None = None
    hard_max_weight: Decimal | None = None

    estimated_post_trade_weight: Decimal | None = None

    sizing_state: str | None = None
    sizing_reason_codes: list[str] | None = None
