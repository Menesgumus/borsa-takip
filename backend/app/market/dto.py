"""Market data DTOs (Data Transfer Objects).

All prices use Decimal for exact arithmetic — never float.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class HistoricalBarDTO(BaseModel):
    """Historical bar data for a single trading session."""
    symbol: str = Field(..., description="Canonical instrument symbol")
    timestamp: datetime = Field(..., description="Session date/time (UTC)")
    open: Decimal = Field(..., description="Session open price")
    high: Decimal = Field(..., description="Session high price")
    low: Decimal = Field(..., description="Session low price")
    close: Decimal = Field(..., description="Session close price")
    volume: int = Field(0, description="Session volume")
    source_name: str = Field(..., description="Provider that produced this data")
    price_basis: str = Field("RAW", description="RAW or ADJUSTED")
    is_adjusted: bool = Field(False, description="True if prices are adjusted for corporate actions")
    source_record_id: str | None = Field(None, description="Provider's internal ID if any")

class QuoteDTO(BaseModel):
    """Snapshot quote from any market data provider.

    `is_stale` is True when the provider's timestamp is older than
    the caller-supplied `max_age_seconds` threshold.
    """

    symbol: str = Field(..., description="Canonical instrument symbol, e.g. 'BIST:GARAN'")
    price: Decimal = Field(..., description="Last traded price")
    change_pct: Decimal = Field(..., description="Day change percentage, e.g. 1.25 = +1.25%")
    volume: int | None = Field(None, description="Day volume (shares/units traded)")
    high: Decimal = Field(..., description="Day high")
    low: Decimal = Field(..., description="Day low")
    open: Decimal = Field(..., description="Day open")
    previous_close: Decimal = Field(..., description="Previous session close")
    timestamp: datetime = Field(..., description="Quote timestamp (UTC)")
    source_name: str = Field(..., description="Provider that produced this quote")
    freshness_seconds: float = Field(
        ..., description="Seconds elapsed since quote timestamp at time of response"
    )
    is_stale: bool = Field(
        False,
        description="True when freshness_seconds exceeds the configured threshold",
    )
    data_state: str = Field(
        "DELAYED",
        description="Canonical state: LIVE, DELAYED, EOD, STALE, UNAVAILABLE, MOCK"
    )
    is_mock: bool = Field(
        False,
        description="True if this is a synthetic mock quote"
    )
    is_adjusted: bool = Field(
        False,
        description="True if this historical price has been adjusted for corporate actions"
    )

    model_config = {"frozen": True}
