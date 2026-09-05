from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PortfolioBase(BaseSchema):
    name: str = Field(..., min_length=1)


class Portfolio(PortfolioBase):
    id: int
    created_at: datetime
    updated_at: datetime


class PositionBase(BaseSchema):
    symbol: str = Field(..., min_length=1)
    quantity: Decimal = Field(default=Decimal("0"))
    average_cost: Decimal = Field(default=Decimal("0"))


class Position(PositionBase):
    id: int
    portfolio_id: int
    created_at: datetime
    updated_at: datetime


class QuoteBase(BaseSchema):
    symbol: str = Field(..., min_length=1)
    price: Decimal


class Quote(QuoteBase):
    id: int
    timestamp: datetime


class TradeBase(BaseSchema):
    symbol: str = Field(..., min_length=1)
    trade_type: str = Field(..., pattern="^(BUY|SELL)$")
    quantity: Decimal
    price: Decimal


class Trade(TradeBase):
    id: int
    portfolio_id: int
    executed_at: datetime
