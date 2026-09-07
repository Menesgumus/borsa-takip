from datetime import datetime

from pydantic import BaseModel


class IndicatorValue(BaseModel):
    timestamp: datetime
    sma_20: float | None = None
    ema_20: float | None = None
    rsi_14: float | None = None
    macd_line: float | None = None
    macd_signal: float | None = None
    macd_hist: float | None = None

class TechnicalAnalysisResponse(BaseModel):
    symbol: str
    freshness: str
    indicators: list[IndicatorValue]
