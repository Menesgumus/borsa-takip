from datetime import datetime

from pydantic import BaseModel


class IndicatorValue(BaseModel):
    timestamp: datetime
    close: float | None = None
    sma_20: float | None = None
    ema_20: float | None = None
    sma_50: float | None = None
    sma_200: float | None = None
    rsi_14: float | None = None
    macd_line: float | None = None
    macd_signal: float | None = None
    macd_hist: float | None = None

class SRLevelDTO(BaseModel):
    price: float
    type: str
    strength: int

class PatternResultDTO(BaseModel):
    pattern_name: str
    timestamp: datetime
    confidence: float
    evidence: str

class TechnicalAnalysisResponse(BaseModel):
    symbol: str
    freshness: str
    indicators: list[IndicatorValue]
    support_resistance: list[SRLevelDTO] = []
    patterns: list[PatternResultDTO] = []
