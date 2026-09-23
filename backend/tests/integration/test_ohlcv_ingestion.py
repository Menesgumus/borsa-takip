import pytest
from datetime import UTC, datetime, timedelta
from sqlalchemy import select
from app.market.historical_ohlcv_ingestor import ingest_ohlcv
from app.db.models import OHLCVDaily, IngestionRun, Instrument, ProviderMapping
from app.db.session import async_session_maker

@pytest.mark.asyncio
async def test_ohlcv_ingestion_idempotency():
    async with async_session_maker() as db_session:
        # Register mock provider
        from app.market.registry import registry
        from app.market.mock_provider import MockMarketDataProvider
        registry.register(MockMarketDataProvider(), is_primary=True)

        # Setup test instrument
        import uuid
        test_symbol = f"TESTBIST_{uuid.uuid4().hex[:8]}"
        inst = Instrument(symbol=test_symbol, name="Test", exchange="BIST", asset_class="BIST_EQUITY", is_active=True)
        db_session.add(inst)
        await db_session.commit()
        await db_session.refresh(inst)

        mapping = ProviderMapping(
            instrument_id=inst.id,
            provider_name="mock",
            provider_symbol=test_symbol,
            is_primary=True
        )
        db_session.add(mapping)
        await db_session.commit()

        start_date = datetime.now(UTC) - timedelta(days=2)
        end_date = datetime.now(UTC)

        # First run
        run1_id = await ingest_ohlcv(
            db=db_session,
            symbols=[test_symbol],
            start_date=start_date,
            end_date=end_date,
            provider_name="mock",
            dataset_type="OHLCV"
        )

        # Assert rows inserted
        result = await db_session.execute(select(OHLCVDaily).where(OHLCVDaily.instrument_id == inst.id))
        rows = result.scalars().all()
        assert len(rows) > 0
        assert rows[0].ingestion_run_id == run1_id

        from app.db.models import OHLCVSourceObservation
        result_src = await db_session.execute(select(OHLCVSourceObservation).where(OHLCVSourceObservation.instrument_id == inst.id))
        src_rows = result_src.scalars().all()
        assert len(src_rows) == len(rows)
        assert src_rows[0].ingestion_run_id == run1_id

        # Second run (idempotent overwrite)
        run2_id = await ingest_ohlcv(
            db=db_session,
            symbols=[test_symbol],
            start_date=start_date,
            end_date=end_date,
            provider_name="mock",
            dataset_type="OHLCV"
        )

        # Assert canonical row count remains same but run ID is updated
        result2 = await db_session.execute(select(OHLCVDaily).where(OHLCVDaily.instrument_id == inst.id))
        rows2 = result2.scalars().all()
        assert len(rows2) == len(rows)
        
        # Verify source observations did NOT multiply because they were exact replays
        result_src2 = await db_session.execute(select(OHLCVSourceObservation).where(OHLCVSourceObservation.instrument_id == inst.id))
        src_rows2 = result_src2.scalars().all()
        assert len(src_rows2) == len(src_rows)
        # Source rows keep original ingestion_run_id because payload didn't change
        assert src_rows2[0].ingestion_run_id == run1_id
        
        # Verify they were updated to the new run ID via a DB query to avoid async lazy load issues
        from sqlalchemy import func
        result_updated = await db_session.execute(
            select(func.count(OHLCVDaily.id))
            .where(OHLCVDaily.instrument_id == inst.id)
            .where(OHLCVDaily.ingestion_run_id == run2_id)
        )
        updated_count = result_updated.scalar()
        assert updated_count == len(rows)
