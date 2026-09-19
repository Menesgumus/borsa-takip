from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from app.db.models import PortfolioType, TransactionType


class PortfolioCreate(BaseModel):
    name: str
    portfolio_type: PortfolioType = PortfolioType.PAPER
    currency: str = "TRY"

class PortfolioRead(PortfolioCreate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PortfolioOverviewDTO(PortfolioRead):
    cash_balance: Decimal
    total_realized_pnl: Decimal
    total_unrealized_pnl: Decimal | None = None
    total_market_value: Decimal | None = None
    data_freshness: str = "LIVE"
    valuation_complete: bool = True

class TransactionCreate(BaseModel):
    transaction_type: TransactionType
    instrument_id: int | None = None
    quantity: Decimal
    price: Decimal = Decimal("0")
    fee: Decimal = Decimal("0")
    executed_at: datetime | None = None
    notes: str | None = None
    strategy: str | None = None
    # Phase 28 Multi-asset fields
    native_price: Decimal | None = None
    native_currency: str | None = None
    fx_rate_to_base: Decimal | None = None
    execution_source: str | None = None

class TransactionRead(TransactionCreate):
    id: int
    portfolio_id: int
    executed_at: datetime
    created_at: datetime
    instrument_symbol: str | None = None

    class Config:
        from_attributes = True

class PortfolioTradeCreate(BaseModel):
    side: Literal["BUY", "SELL"]
    instrument_id: int
    quantity: Decimal | None = None
    budget_amount: Decimal | None = None

class ManualTradeCreate(BaseModel):
    side: Literal["BUY", "SELL"]
    instrument_id: int
    quantity: Decimal
    native_execution_price: Decimal
    fee: Decimal = Decimal("0")
    executed_at: datetime | None = None

class PositionDTO(BaseModel):
    instrument_id: int
    symbol: str
    name: str
    quantity: Decimal
    average_cost: Decimal
    realized_pnl: Decimal
    current_price: Decimal | None = None
    market_value: Decimal | None = None
    unrealized_pnl: Decimal | None = None
    # Multi-asset fields
    asset_class: str | None = None
    native_currency: str | None = None
    average_cost_native: Decimal | None = None
    current_native_price: Decimal | None = None
    current_fx_rate_to_base: Decimal | None = None

class PortfolioSummaryDTO(BaseModel):
    portfolio_id: int
    cash_balance: Decimal
    total_deposits: Decimal
    total_withdrawals: Decimal
    total_realized_pnl: Decimal
    total_unrealized_pnl: Decimal | None = None
    total_market_value: Decimal | None = None
    market_data_freshness: str = "DELAYED"
    valuation_complete: bool = True
    positions: list[PositionDTO]

class TradeJournalCreate(BaseModel):
    transaction_id: int | None = None
    setup: str | None = None
    reason: str | None = None
    emotion: str | None = None
    lessons_learned: str | None = None

class TradeJournalRead(TradeJournalCreate):
    id: int
    portfolio_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SleeveAllocationDTO(BaseModel):
    asset_class: str
    current_value: Decimal
    current_weight: Decimal
    target_weight: Decimal
    target_value: Decimal
    deficit_value: Decimal
    proposed_allocation: Decimal
    unallocated_reason: str | None = None

class BasketItemDTO(BaseModel):
    instrument_id: int
    symbol: str
    name: str
    asset_class: str
    native_currency: str
    market_view: str
    personal_action: str
    market_score: int
    data_quality_score: int
    analysis_native_price: Decimal
    fx_rate_to_base: Decimal
    analysis_base_price: Decimal
    proposed_quantity: Decimal
    proposed_native_budget: Decimal
    proposed_base_budget: Decimal
    projected_weight: Decimal
    recommended_target_weight: Decimal
    hard_max_weight: Decimal
    sizing_state: str
    reason_codes: list[str]

class BasketPreviewResponse(BaseModel):
    portfolio_id: int
    base_currency: str
    risk_tolerance: str
    allocation_policy_version: str
    portfolio_total_value: Decimal
    available_cash: Decimal
    requested_deploy_amount: Decimal
    allocated_amount: Decimal
    unallocated_amount: Decimal
    target_cash_reserve: Decimal
    constraint_unallocated: Decimal
    valuation_complete: bool
    data_state: str
    sleeves: list[SleeveAllocationDTO]
    items: list[BasketItemDTO]

class BasketPreviewRequest(BaseModel):
    deploy_amount: Decimal

class ExecutionPreviewRequest(BaseModel):
    instrument_id: int
    manual_native_price: Decimal

class ExecutionPreviewResponse(BaseModel):
    analysis_price: Decimal
    analysis_price_state: str
    execution_price: Decimal
    execution_source: str
    execution_currency: str
    fx_rate: Decimal
    fx_source: str
    fx_as_of: datetime | None = None
    recomputed_quantity: Decimal
    recomputed_budget: Decimal
    projected_weight: Decimal
    market_view: str
    personal_action: str
    market_score: int
