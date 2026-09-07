from datetime import datetime
from decimal import Decimal

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

class TransactionCreate(BaseModel):
    transaction_type: TransactionType
    instrument_id: int | None = None
    quantity: Decimal
    price: Decimal = Decimal("0")
    fee: Decimal = Decimal("0")
    executed_at: datetime | None = None
    notes: str | None = None
    strategy: str | None = None

class TransactionRead(TransactionCreate):
    id: int
    portfolio_id: int
    executed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

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

class PortfolioSummaryDTO(BaseModel):
    portfolio_id: int
    cash_balance: Decimal
    total_deposits: Decimal
    total_withdrawals: Decimal
    total_realized_pnl: Decimal
    total_unrealized_pnl: Decimal | None = None
    total_market_value: Decimal | None = None
    market_data_freshness: str = "LIVE"
    positions: list[PositionDTO]
