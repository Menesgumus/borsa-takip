import pytest
from sqlalchemy import text
from app.db.session import async_session_maker

@pytest.mark.asyncio
async def test_canonical_schema_tables_exist():
    # Verify the new tables exist
    tables = [
        "ingestion_runs",
        "trading_sessions",
        "historical_fx_rates",
        "benchmark_series",
        "corporate_actions",
        "instrument_universe_history",
        "dataset_snapshots"
    ]
    
    async with async_session_maker() as db_session:
        for table in tables:
            # Check if table exists by querying it
            result = await db_session.execute(text(f"SELECT 1 FROM {table} LIMIT 0"))
            assert result is not None

@pytest.mark.asyncio
async def test_ohlcv_provenance_columns():
    async with async_session_maker() as db_session:
        # Verify the new columns exist in ohlcv_daily
        result = await db_session.execute(
            text("SELECT ingestion_run_id, provenance_type, is_adjusted, session_type, source_record_id FROM ohlcv_daily LIMIT 0")
        )
        assert result is not None

@pytest.mark.asyncio
async def test_fundamental_revision_column():
    async with async_session_maker() as db_session:
        # Verify the new columns exist in fundamental_data
        result = await db_session.execute(
            text("SELECT revision, ingestion_run_id, provenance_type FROM fundamental_data LIMIT 0")
        )
        assert result is not None

@pytest.mark.asyncio
async def test_calibration_cycle_snapshot_column():
    async with async_session_maker() as db_session:
        # Verify the new column exists in calibration_cycles
        result = await db_session.execute(
            text("SELECT dataset_snapshot_id FROM calibration_cycles LIMIT 0")
        )
        assert result is not None
