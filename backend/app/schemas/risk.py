from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class PositionExposure(BaseModel):
    instrument_id: int
    symbol: str
    weight_percentage: Decimal
    market_value: Decimal
    is_stale: bool

class LimitViolation(BaseModel):
    rule_name: str
    limit_value: Decimal
    actual_value: Decimal
    reason_code: str

class PortfolioRiskMetrics(BaseModel):
    portfolio_id: int
    total_market_value: Decimal
    invested_exposure: Decimal
    cash_exposure: Decimal
    cash_weight_percentage: Decimal
    invested_weight_percentage: Decimal

    # Advanced metrics
    historical_var_95_1d: Decimal | None = None
    annualized_volatility: Decimal | None = None
    max_drawdown: Decimal | None = None

    positions_exposure: list[PositionExposure]
    limit_violations: list[LimitViolation]

    # Metadata
    calculated_at: datetime
    data_freshness: str  # LIVE, STALE, UNAVAILABLE
    coverage_percentage: Decimal  # % of invested amount with live quotes

class WhatIfRequest(BaseModel):
    transaction_type: str # BUY, SELL
    instrument_id: int
    quantity: Decimal
    price: Decimal
    fee: Decimal = Decimal("0")

class WhatIfResponse(BaseModel):
    before_risk: PortfolioRiskMetrics
    after_risk: PortfolioRiskMetrics
    delta_var_95_1d: Decimal | None = None
    delta_invested_exposure: Decimal
    newly_triggered_limits: list[LimitViolation]
    resolved_limits: list[LimitViolation]
