import enum
from pydantic import BaseModel
from typing import List, Optional, Dict
from decimal import Decimal
from datetime import datetime
from app.db.models import DecisionAction

class Horizon(str, enum.Enum):
    SHORT = "SHORT"
    MEDIUM = "MEDIUM"
    LONG = "LONG"

class TechnicalInputs(BaseModel):
    rsi_14: Optional[Decimal] = None
    macd_line: Optional[Decimal] = None
    macd_signal: Optional[Decimal] = None
    sma_50: Optional[Decimal] = None
    sma_200: Optional[Decimal] = None
    current_price: Optional[Decimal] = None
    is_stale: bool = False

class FundamentalInputs(BaseModel):
    pe_ratio: Optional[Decimal] = None # F/K
    pb_ratio: Optional[Decimal] = None # PD/DD
    instrument_type: str = "STOCK" # STOCK, CRYPTO, FX, etc.

class NewsInputs(BaseModel):
    sentiment_score: Optional[Decimal] = None # 0 to 100, 50 is neutral
    news_count: int = 0
    is_mock: bool = False

class PortfolioFitInputs(BaseModel):
    current_weight: Decimal = Decimal("0") # 0 to 100
    max_weight_limit: Decimal = Decimal("100") # 0 to 100
    portfolio_risk_level: str = "MODERATE"

class DecisionResult(BaseModel):
    instrument_id: int
    horizon: Horizon
    as_of: datetime
    
    technical_score: Optional[Decimal] = None     # 0-100
    fundamental_score: Optional[Decimal] = None   # 0-100
    news_score: Optional[Decimal] = None          # 0-100
    risk_reward_score: Optional[Decimal] = None   # 0-100
    portfolio_fit_score: Optional[Decimal] = None # 0-100
    data_quality_score: Decimal                   # 0-100
    
    overall_market_score: Decimal                 # 0-100
    overall_personal_score: Optional[Decimal] = None # 0-100
    
    market_view: DecisionAction
    personal_action: Optional[DecisionAction] = None
    
    reason_codes: List[str]
    warnings: List[str]
    
    missing_data: bool
    engine_version: str
