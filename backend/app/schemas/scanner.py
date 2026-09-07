from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OpportunityResult(BaseModel):
    instrument_symbol: str
    instrument_name: str

    raw_score: Decimal
    market_view: str

    user_fit_score: Decimal | None = None
    personal_action: str | None = None

    reasons: list[str]
    warnings: list[str]
    missing_data: bool
    calculated_at: datetime
    engine_version: str
