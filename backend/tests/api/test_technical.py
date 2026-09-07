import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone, timedelta
from app.main import app
from app.db.models import Instrument, OHLCVDaily
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_get_technical_analysis(
    db_session: AsyncSession,
    client: AsyncClient
):
    # 1. Create instrument
    instrument = Instrument(
        symbol="TECH",
        name="Tech Analysis Corp",
        exchange="BIST",
        instrument_type="EQUITY",
        is_active=True
    )
    db_session.add(instrument)
    await db_session.commit()
    
    # 2. Add some OHLCV data
    base_date = datetime.now(timezone.utc) - timedelta(days=50)
    for i in range(50):
        candle = OHLCVDaily(
            instrument_id=instrument.id,
            timestamp=base_date + timedelta(days=i),
            open=100.0 + i,
            high=105.0 + i,
            low=95.0 + i,
            close=100.0 + i,
            volume=1000
        )
        db_session.add(candle)
    await db_session.commit()
    
    # 3. Call endpoint
    response = await client.get("/api/v1/instruments/TECH/technical")
    assert response.status_code == 200
    data = response.json()
    
    assert data["symbol"] == "TECH"
    assert data["freshness"] == "LIVE"
    assert len(data["indicators"]) == 50
    
    # Check that SMA is populated correctly
    # i=0 to i=18 should be None
    assert data["indicators"][0]["sma_20"] is None
    assert data["indicators"][19]["sma_20"] is not None
