import logging
from datetime import datetime
from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Instrument, OHLCVDaily
from app.schemas.technical import (
    IndicatorValue,
    PatternResultDTO,
    SRLevelDTO,
    TechnicalAnalysisResponse,
)
from app.technical.indicators import calculate_ema, calculate_macd, calculate_rsi, calculate_sma
from app.technical.patterns import detect_patterns
from app.technical.support_resistance import calculate_support_resistance

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
        return TechnicalAnalysisResponse(symbol=symbol, freshness="STALE", indicators=[], support_resistance=[], patterns=[])

    opens = [float(c.open) for c in candles]
    highs = [float(c.high) for c in candles]
    lows = [float(c.low) for c in candles]
    closes = [float(c.close) for c in candles]
    timestamps = [cast(datetime, c.timestamp) for c in candles]

    sma_20 = calculate_sma(closes, 20)
    ema_20 = calculate_ema(closes, 20)
    sma_50 = calculate_sma(closes, 50)
    sma_200 = calculate_sma(closes, 200)
    rsi_14 = calculate_rsi(closes, 14)
    macd_res = calculate_macd(closes, 12, 26, 9)

    sr_levels = calculate_support_resistance(highs, lows, window=5, cluster_threshold_pct=1.5)
    pattern_results = detect_patterns(opens, highs, lows, closes)

    indicators: list[IndicatorValue] = []

    for i in range(len(candles)):
        # To avoid massive payload, we can limit to recent history if we wanted,
        # but here we just return what is calculated. We only skip if all are None.
        if start_date and timestamps[i] < start_date:
            continue
        if (sma_20[i] is None and ema_20[i] is None and rsi_14[i] is None and macd_res[i].macd_line is None):
            continue

        indicators.append(
            IndicatorValue(
                timestamp=timestamps[i],
                close=closes[i],
                sma_20=sma_20[i],
                ema_20=ema_20[i],
                sma_50=sma_50[i],
                sma_200=sma_200[i],
                rsi_14=rsi_14[i],
                macd_line=macd_res[i].macd_line,
                macd_signal=macd_res[i].signal_line,
                macd_hist=macd_res[i].histogram,
            )
        )

    sr_dtos = [SRLevelDTO(price=l.price, type=l.type, strength=l.strength) for l in sr_levels]

    pattern_dtos = []
    for p in pattern_results:
        pt = timestamps[p.index]
        if start_date and pt < start_date:
            continue
        pattern_dtos.append(
            PatternResultDTO(
                pattern_name=p.pattern_name,
                timestamp=pt,
                confidence=p.confidence,
                evidence=p.evidence
            )
        )

    return TechnicalAnalysisResponse(
        symbol=symbol,
        freshness="DELAYED",
        indicators=indicators,
        support_resistance=sr_dtos,
        patterns=pattern_dtos
    )
