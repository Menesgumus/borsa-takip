from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class OpportunityResult(BaseModel):
    instrument_symbol: str
    instrument_name: str
    
    raw_score: Decimal
    market_view: str
    
    user_fit_score: Optional[Decimal] = None
    personal_action: Optional[str] = None
    
    reasons: List[str]
    warnings: List[str]
    missing_data: bool
    calculated_at: datetime
    engine_version: str
