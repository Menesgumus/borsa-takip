import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Instrument, OHLCVDaily
from app.schemas.technical import IndicatorValue, TechnicalAnalysisResponse
from app.technical.indicators import calculate_ema, calculate_macd, calculate_rsi, calculate_sma

logger = logging.getLogger(__name__)

async def get_technical_analysis(
    db: AsyncSession, symbol: str, start_date: datetime | None = None, end_date: datetime | None = None
) -> TechnicalAnalysisResponse:
    result = await db.execute(
        select(Instrument).where(Instrument.symbol == symbol, Instrument.is_active.is_(True))
    )
    instrument = result.scalar_one_or_none()
    if not instrument:
        raise ValueError("Instrument not found")

    stmt = select(OHLCVDaily).where(OHLCVDaily.instrument_id == instrument.id).order_by(OHLCVDaily.timestamp.asc())
    if end_date:
        stmt = stmt.where(OHLCVDaily.timestamp <= end_date)

    history_result = await db.execute(stmt)
    candles = list(history_result.scalars().all())

    if not candles:
        return TechnicalAnalysisResponse(symbol=symbol, freshness="STALE", indicators=[])

    closes = [float(c.close) for c in candles]
    # cast to datetime to satisfy mypy
    timestamps = [c.timestamp for c in candles]

    sma_20 = calculate_sma(closes, 20)
    ema_20 = calculate_ema(closes, 20)
    rsi_14 = calculate_rsi(closes, 14)
    macd_res = calculate_macd(closes, 12, 26, 9)

    indicators: list[IndicatorValue] = []

    for i in range(len(candles)):
        if start_date and timestamps[i] < start_date: # type: ignore
            continue

        indicators.append(
            IndicatorValue(
                timestamp=timestamps[i], # type: ignore
                sma_20=sma_20[i],
                ema_20=ema_20[i],
                rsi_14=rsi_14[i],
                macd_line=macd_res[i].macd_line,
                macd_signal=macd_res[i].signal_line,
                macd_hist=macd_res[i].histogram,
            )
        )

    return TechnicalAnalysisResponse(
        symbol=symbol,
        freshness="LIVE",
        indicators=indicators
    )
