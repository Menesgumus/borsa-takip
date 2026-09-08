import enum
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.db.models import DecisionAction


class Horizon(str, enum.Enum):
    SHORT = "SHORT"
    MEDIUM = "MEDIUM"
    LONG = "LONG"

class TechnicalInputs(BaseModel):
    rsi_14: Decimal | None = None
    macd_line: Decimal | None = None
    macd_signal: Decimal | None = None
    sma_50: Decimal | None = None
    sma_200: Decimal | None = None
    current_price: Decimal | None = None
    is_stale: bool = False

class FundamentalInputs(BaseModel):
    pe_ratio: Decimal | None = None # F/K
    pb_ratio: Decimal | None = None # PD/DD
    instrument_type: str = "STOCK" # STOCK, CRYPTO, FX, etc.

class NewsInputs(BaseModel):
    sentiment_score: Decimal | None = None # 0 to 100, 50 is neutral
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

    technical_score: Decimal | None = None     # 0-100
    fundamental_score: Decimal | None = None   # 0-100
    news_score: Decimal | None = None          # 0-100
    risk_reward_score: Decimal | None = None   # 0-100
    portfolio_fit_score: Decimal | None = None # 0-100
    data_quality_score: Decimal                   # 0-100

    overall_market_score: Decimal                 # 0-100
    overall_personal_score: Decimal | None = None # 0-100

    decision_state: str = "AVAILABLE"
    market_view: DecisionAction
    personal_action: DecisionAction | None = None

    reason_codes: list[str]
    warnings: list[str]

    missing_data: bool
    engine_version: str
