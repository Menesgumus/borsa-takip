import asyncio
from datetime import UTC, datetime
import logging
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import IngestionRun, OHLCVDaily, Instrument, ProviderMapping, OHLCVSourceObservation
from app.market.registry import MarketDataRegistry

logger = logging.getLogger(__name__)

async def ingest_ohlcv(
    db: AsyncSession,
    symbols: list[str],
    start_date: datetime,
    end_date: datetime,
    provider_name: str,
    dataset_type: str = "OHLCV",
    concurrency: int = 3
) -> int:
    """
    Ingest historical OHLCV data for given symbols with full provenance.
    Returns the IngestionRun ID.
    """
    import subprocess
    try:
        code_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        code_sha = None

    # 1. Create IngestionRun
    run = IngestionRun(
        provider_name=provider_name,
        dataset_type=dataset_type,
        started_at=datetime.now(UTC),
        status="RUNNING",
        requested_start=start_date,
        requested_end=end_date,
        code_sha=code_sha
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    # Use global registry which should be populated by the app or tests
    from app.market.registry import registry
    semaphore = asyncio.Semaphore(concurrency)
    
    # 2. Get instrument IDs mapping
    instrument_map = {}
    result = await db.execute(select(Instrument).where(Instrument.symbol.in_(symbols)))
    for inst in result.scalars():
        instrument_map[inst.symbol] = inst.id

    rows_received = 0
    rows_inserted = 0
    rows_replayed = 0
    rows_corrected = 0
    rows_canonicalized = 0
    rows_rejected = 0
    
    async def process_symbol(symbol: str):
        nonlocal rows_received, rows_inserted, rows_replayed, rows_corrected, rows_canonicalized, rows_rejected
        if symbol not in instrument_map:
            logger.warning(f"Symbol {symbol} not found in DB")
            return
            
        instrument_id = instrument_map[symbol]
        
        # Resolve provider symbol
        result = await db.execute(
            select(ProviderMapping)
            .where(ProviderMapping.instrument_id == instrument_id)
            .where(ProviderMapping.provider_name == provider_name)
        )
        mapping = result.scalars().first()
        if not mapping:
            logger.warning(f"No provider mapping found for {symbol} under {provider_name}")
            return
            
        provider_symbol = mapping.provider_symbol
        
        async with semaphore:
            try:
                provider = registry.get_provider(provider_name)
                bars = await provider.get_historical_quotes(
                    symbol=provider_symbol,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if not bars:
                    return

                rows_received += len(bars)
                
                # Fetch existing latest source observations for this instrument and provider
                from sqlalchemy import desc
                stmt = (
                    select(OHLCVSourceObservation)
                    .where(OHLCVSourceObservation.instrument_id == instrument_id)
                    .where(OHLCVSourceObservation.provider_name == provider_name)
                    .order_by(OHLCVSourceObservation.timestamp, desc(OHLCVSourceObservation.retrieved_at))
                )
                existing_obs_result = await db.execute(stmt)
                
                # Build dict of timestamp -> latest observation
                existing_obs = {}
                for obs in existing_obs_result.scalars():
                    # We only care about the most recent observation for a timestamp
                    if obs.timestamp not in existing_obs:
                        existing_obs[obs.timestamp] = obs

                source_values = []
                canonical_values = []
                
                for b in bars:
                    payload_changed = True
                    is_new = True
                    
                    if b.timestamp in existing_obs:
                        is_new = False
                        old = existing_obs[b.timestamp]
                        # Exact replay check
                        if (old.open == b.open and old.high == b.high and 
                            old.low == b.low and old.close == b.close and 
                            old.volume == b.volume and old.is_adjusted == b.is_adjusted and
                            old.price_basis == b.price_basis):
                            payload_changed = False
                    
                    if payload_changed:
                        if is_new:
                            rows_inserted += 1
                        else:
                            rows_corrected += 1
                            
                        # Insert new source observation
                        source_values.append({
                            "instrument_id": instrument_id,
                            "timestamp": b.timestamp,
                            "provider_name": b.source_name,
                            "provider_symbol": provider_symbol,
                            "open": b.open,
                            "high": b.high,
                            "low": b.low,
                            "close": b.close,
                            "volume": b.volume,
                            "is_adjusted": b.is_adjusted,
                            "price_basis": b.price_basis,
                            "ingestion_run_id": run.id,
                            "source_record_id": b.source_record_id,
                        })
                    else:
                        rows_replayed += 1
                    
                    # We ALWAYS canonicalize RAW prices for the canonical layer
                    if b.price_basis == "RAW":
                        canonical_values.append({
                            "instrument_id": instrument_id,
                            "timestamp": b.timestamp,
                            "open": b.open,
                            "high": b.high,
                            "low": b.low,
                            "close": b.close,
                            "volume": b.volume,
                            "provider_name": b.source_name,
                            "ingestion_run_id": run.id,
                            "provenance_type": "PRIMARY_INGEST",
                            "is_adjusted": b.is_adjusted,
                            "session_type": "REGULAR"
                        })
                
                if source_values:
                    await db.execute(insert(OHLCVSourceObservation).values(source_values))
                
                if canonical_values:
                    stmt_can = insert(OHLCVDaily).values(canonical_values)
                    stmt_can = stmt_can.on_conflict_do_update(
                        index_elements=["instrument_id", "timestamp"],
                        set_={
                            "open": stmt_can.excluded.open,
                            "high": stmt_can.excluded.high,
                            "low": stmt_can.excluded.low,
                            "close": stmt_can.excluded.close,
                            "volume": stmt_can.excluded.volume,
                            "provider_name": stmt_can.excluded.provider_name,
                            "ingestion_run_id": stmt_can.excluded.ingestion_run_id,
                            "provenance_type": stmt_can.excluded.provenance_type,
                            "is_adjusted": stmt_can.excluded.is_adjusted,
                            "session_type": stmt_can.excluded.session_type,
                            "updated_at": func.now()
                        }
                    )
                    await db.execute(stmt_can)
                    rows_canonicalized += len(canonical_values)
                
                await db.commit()

            except Exception as e:
                logger.error(f"Error ingesting {symbol}: {e}")
                rows_rejected += 1

    # 3. Process all symbols concurrently
    tasks = [process_symbol(s) for s in symbols]
    await asyncio.gather(*tasks)

    # 4. Finalize IngestionRun
    run.finished_at = datetime.now(UTC)
    run.status = "COMPLETED" if rows_rejected == 0 else "PARTIAL"
    if rows_received == 0:
        run.status = "NO_DATA"
        
    run.rows_received = rows_received
    # Storing metrics in generic fields for schema compatibility
    run.rows_inserted = rows_inserted
    run.rows_updated = rows_corrected
    run.rows_rejected = rows_rejected
    
    await db.commit()
    return run.id
