import hashlib
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import OHLCVDaily, FundamentalData, Instrument
from app.services.canonical import canonicalize

async def get_dataset_fingerprint(db: AsyncSession, instrument_ids: list[int] = None) -> str:
    # 1. Fetch Instruments (Universe)
    query = select(Instrument)
    if instrument_ids:
        query = query.where(Instrument.id.in_(instrument_ids))
    res = await db.execute(query)
    instruments = res.scalars().all()
    
    components = []
    
    # Versioning structure
    components.append(("SCHEMA_VERSION", "1.0.0"))
    
    # Add explicit limitations for unavailable data classes
    components.append(("HISTORICAL_FX_SERIES", "LIMITED_BY_DATA"))
    components.append(("CORPORATE_ACTIONS", "LIMITED_BY_DATA"))
    components.append(("HISTORICAL_UNIVERSE_MEMBERSHIP", "LIMITED_BY_DATA"))
    components.append(("BENCHMARK_SERIES", "LIMITED_BY_DATA"))
    
    for inst in instruments:
        inst_canon = f"{inst.exchange}|{inst.symbol}|{canonicalize(inst.instrument_type)}|{inst.currency}"
        
        # OHLCV
        res_ohlcv = await db.execute(select(OHLCVDaily).where(OHLCVDaily.instrument_id == inst.id))
        for ohlcv in res_ohlcv.scalars().all():
            comp = (
                "OHLCV",
                inst_canon,
                canonicalize(ohlcv.timestamp),
                canonicalize(ohlcv.open),
                canonicalize(ohlcv.high),
                canonicalize(ohlcv.low),
                canonicalize(ohlcv.close),
                canonicalize(ohlcv.volume)
            )
            components.append(comp)
            
        # Fundamentals
        res_fund = await db.execute(select(FundamentalData).where(FundamentalData.instrument_id == inst.id))
        for fund in res_fund.scalars().all():
            comp = (
                "FUNDAMENTAL",
                inst_canon,
                canonicalize(fund.period),
                canonicalize(fund.period_end),
                canonicalize(fund.published_at),
                canonicalize(fund.available_at),
                canonicalize(fund.source),
                canonicalize(fund.pe_ratio),
                canonicalize(fund.pb_ratio),
                canonicalize(fund.market_cap),
                canonicalize(fund.net_income),
                canonicalize(fund.revenue)
            )
            components.append(comp)
            
    # Sort deterministically
    components.sort()
    canonical_string = json.dumps(components, separators=(',', ':'))
    return hashlib.sha256(canonical_string.encode('utf-8')).hexdigest()
