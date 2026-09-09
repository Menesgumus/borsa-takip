from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import Instrument, InstrumentType, OHLCVDaily, User
from app.db.session import async_session_maker
from app.main import app


async def override_get_current_user():
    return User(id=1, email="test@example.com")

@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_technical_analysis():
    async with async_session_maker() as db_session:
        # 1. Create instrument
        import uuid

        sym = f"TECH_{uuid.uuid4().hex[:4]}"
        instrument = Instrument(
            symbol=sym,
            name="Tech Analysis Corp",
            exchange="BIST",
            instrument_type=InstrumentType.STOCK,
            is_active=True
        )
        db_session.add(instrument)
        await db_session.commit()

        # 2. Add some OHLCV data
        base_date = datetime.now(UTC) - timedelta(days=50)
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
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/instruments/{sym}/technical")

    assert response.status_code == 200
    data = response.json()

    assert data["symbol"] == sym
    assert data["freshness"] == "DELAYED"
    assert len(data["indicators"]) > 0

    # Check that SMA is populated correctly
    assert data["indicators"][0]["sma_20"] is None
    assert data["indicators"][19]["sma_20"] is not None
