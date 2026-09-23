import asyncio
from datetime import UTC, datetime
import logging
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import IngestionRun, OHLCVDaily, Instrument, ProviderMapping
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
    # 1. Create IngestionRun
    run = IngestionRun(
        provider_name=provider_name,
        dataset_type=dataset_type,
        started_at=datetime.now(UTC),
        status="RUNNING",
        requested_start=start_date,
        requested_end=end_date,
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
    rows_updated = 0
    rows_rejected = 0
    
    async def process_symbol(symbol: str):
        nonlocal rows_received, rows_inserted, rows_updated, rows_rejected
        if symbol not in instrument_map:
            logger.warning(f"Symbol {symbol} not found in DB")
            rows_rejected += 1
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
            rows_rejected += 1
            return
            
        provider_symbol = mapping.provider_symbol
        
        async with semaphore:
            try:
                # get_historical_quotes returns QuoteDTO
                provider = registry.get_provider(provider_name)
                quotes = await provider.get_historical_quotes(
                    symbol=provider_symbol,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if not quotes:
                    return

                rows_received += len(quotes)
                
                # Bulk upsert
                values = []
                for q in quotes:
                    values.append({
                        "instrument_id": instrument_id,
                        "timestamp": q.timestamp,
                        "open": q.open,
                        "high": q.high,
                        "low": q.low,
                        "close": q.price,
                        "volume": q.volume,
                        "provider_name": q.source_name,
                        "ingestion_run_id": run.id,
                        "provenance_type": "PRIMARY_INGEST",
                        "is_adjusted": q.is_adjusted,
                        "session_type": "REGULAR"
                    })
                
                stmt = insert(OHLCVDaily).values(values)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["instrument_id", "timestamp"],
                    set_={
                        "open": stmt.excluded.open,
                        "high": stmt.excluded.high,
                        "low": stmt.excluded.low,
                        "close": stmt.excluded.close,
                        "volume": stmt.excluded.volume,
                        "provider_name": stmt.excluded.provider_name,
                        "ingestion_run_id": stmt.excluded.ingestion_run_id,
                        "provenance_type": stmt.excluded.provenance_type,
                        "is_adjusted": stmt.excluded.is_adjusted,
                        "session_type": stmt.excluded.session_type,
                        "updated_at": func.now()
                    }
                )
                
                await db.execute(stmt)
                await db.commit()
                # We count as upserted, accurate counting of insert vs update requires more complex logic
                rows_updated += len(quotes)

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
    run.rows_inserted = rows_inserted
    run.rows_updated = rows_updated
    run.rows_rejected = rows_rejected
    
    await db.commit()
    return run.id
