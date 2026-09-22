import hashlib
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
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
    
    for inst in instruments:
        inst_canon = f"{inst.exchange}|{inst.symbol}|{canonicalize(inst.asset_class)}|{inst.currency}"
        
        # OHLCV
        res_ohlcv = await db.execute(select(OHLCVDaily).where(OHLCVDaily.instrument_id == inst.id))
        for ohlcv in res_ohlcv.scalars().all():
            comp = (
                "OHLCV",
                inst_canon,
                canonicalize(ohlcv.timestamp),
                canonicalize(ohlcv.open_price),
                canonicalize(ohlcv.high_price),
                canonicalize(ohlcv.low_price),
                canonicalize(ohlcv.close_price),
                canonicalize(ohlcv.volume),
                canonicalize(ohlcv.data_state)
            )
            components.append(comp)
            
        # Fundamentals
        res_fund = await db.execute(select(FundamentalData).where(FundamentalData.instrument_id == inst.id))
        for fund in res_fund.scalars().all():
            comp = (
                "FUNDAMENTAL",
                inst_canon,
                canonicalize(fund.timestamp),
                canonicalize(fund.publication_timestamp),
                canonicalize(fund.pe_ratio),
                canonicalize(fund.pb_ratio),
                canonicalize(fund.roe),
                canonicalize(fund.debt_to_equity),
                canonicalize(fund.data_state)
            )
            components.append(comp)
            
    # Sort deterministically
    components.sort()
    canonical_string = json.dumps(components, separators=(',', ':'))
    return hashlib.sha256(canonical_string.encode('utf-8')).hexdigest()
