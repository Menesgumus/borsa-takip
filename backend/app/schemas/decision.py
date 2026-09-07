from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from app.db.models import DecisionAction

class TechnicalInputs(BaseModel):
    rsi_14: Optional[Decimal] = None
    macd_line: Optional[Decimal] = None
    macd_signal: Optional[Decimal] = None
    sma_50: Optional[Decimal] = None
    sma_200: Optional[Decimal] = None
    current_price: Optional[Decimal] = None

class FundamentalInputs(BaseModel):
    pe_ratio: Optional[Decimal] = None # F/K
    pb_ratio: Optional[Decimal] = None # PD/DD

class DecisionResult(BaseModel):
    instrument_id: int
    action: DecisionAction
    score: Decimal
    reason_codes: List[str]
    missing_data: bool
    engine_version: str
