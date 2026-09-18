import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Instrument, OHLCVDaily
from app.schemas.decision import TechnicalInputs
from app.technical.indicators import calculate_macd, calculate_rsi, calculate_sma

logger = logging.getLogger(__name__)

async def get_batched_technical_inputs(
    db: AsyncSession,
    symbols: list[str]
) -> dict[str, TechnicalInputs | None]:
    """
    Efficiently fetches the last 250 days of OHLCV data for all requested symbols,
    and computes ONLY the TechnicalInputs required by the decision engine.
    Returns a dictionary mapping symbol -> TechnicalInputs.
    """
    if not symbols:
        return {}

    # Get instruments map
    res = await db.execute(
        select(Instrument).where(Instrument.symbol.in_(symbols), Instrument.is_active.is_(True))
    )
    instruments = list(res.scalars().all())
    inst_map = {inst.id: inst.symbol for inst in instruments}
    inst_ids = list(inst_map.keys())

    if not inst_ids:
        return {s: None for s in symbols}

    from sqlalchemy import and_, func

    subq = (
        select(
            OHLCVDaily.id,
            func.row_number().over(
                partition_by=OHLCVDaily.instrument_id,
                order_by=OHLCVDaily.timestamp.desc()
            ).label("rn")
        )
        .where(OHLCVDaily.instrument_id.in_(inst_ids))
        .subquery()
    )

    stmt = (
        select(OHLCVDaily)
        .join(subq, and_(OHLCVDaily.id == subq.c.id, subq.c.rn <= 250))
        .order_by(OHLCVDaily.instrument_id, OHLCVDaily.timestamp.asc())
    )

    r = await db.execute(stmt)
    all_candles = r.scalars().all()

    # Group by instrument_id
    from collections import defaultdict
    candles_by_inst = defaultdict(list)
    for c in all_candles:
        candles_by_inst[c.instrument_id].append(c)

    tech_map: dict[str, TechnicalInputs | None] = {}

    for inst_id in inst_ids:
        symbol = str(inst_map[inst_id])
        candles = candles_by_inst.get(inst_id, [])
        if not candles:
            tech_map[symbol] = None
            continue

        closes = [float(c.close) for c in candles]
        if not closes:
            tech_map[symbol] = None
            continue

        current_price = Decimal(str(closes[-1]))

        rsi_14 = calculate_rsi(closes, 14)
        macd = calculate_macd(closes)
        sma_50 = calculate_sma(closes, 50)
        sma_200 = calculate_sma(closes, 200)

        def safe_dec(arr, idx) -> Decimal | None:
            if not arr or idx >= len(arr) or arr[idx] is None:
                return None
            return Decimal(str(arr[idx]))

        rsi_val = safe_dec(rsi_14, -1)

        macd_line_arr = [m.macd_line for m in macd] if macd else []
        macd_sig_arr = [m.signal_line for m in macd] if macd else []

        macd_line = safe_dec(macd_line_arr, -1)
        macd_sig = safe_dec(macd_sig_arr, -1)
        sma50_val = safe_dec(sma_50, -1)
        sma200_val = safe_dec(sma_200, -1)

        tech_map[symbol] = TechnicalInputs(
            current_price=current_price,
            rsi_14=rsi_val,
            macd_line=macd_line,
            macd_signal=macd_sig,
            sma_50=sma50_val,
            sma_200=sma200_val
        )

    for s in symbols:
        if s not in tech_map:
            tech_map[s] = None

    return tech_map
