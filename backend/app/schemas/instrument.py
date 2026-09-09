from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class InstrumentBase(BaseModel):
    symbol: str
    name: str
    exchange: str
    instrument_type: str
    is_active: bool = True


class InstrumentResponse(InstrumentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InstrumentsPaginated(BaseModel):
    items: list[InstrumentResponse]
    total: int
    page: int
    size: int


class OHLCVDailyResponse(BaseModel):
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int | None
    provider_name: str | None

    model_config = ConfigDict(from_attributes=True)

from typing import Literal

from app.market.dto import QuoteDTO


class BatchQuoteItem(BaseModel):
    """Status-wrapped quote item for batch responses."""
    symbol: str
    status: Literal["AVAILABLE", "UNAVAILABLE", "PROVIDER_ERROR", "TIMEOUT", "NOT_FOUND"]
    quote: QuoteDTO | None = None
    error_code: str | None = None


class BatchQuoteResponse(BaseModel):
    """Batch quote response with per-symbol availability status."""
    items: dict[str, BatchQuoteItem]
    requested_count: int
    available_count: int
    unavailable_count: int
    as_of: datetime
