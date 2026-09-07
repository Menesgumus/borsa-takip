import random
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import Instrument, InstrumentType, Portfolio, User
from app.db.session import async_session_maker
from app.main import app

user_mock_data = {}
async def override_get_current_user():
    async with async_session_maker() as db_session:
        user = await db_session.get(User, user_mock_data["user_id"])
        return user

@pytest.mark.asyncio
async def test_opportunities_scanner_api():
    async with async_session_maker() as db_session:
        user = User(id=random.randint(100000, 999999), email=f"scan_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        user_mock_data["user_id"] = user.id

        # Add instruments
        inst1 = Instrument(symbol=f"S1_{uuid.uuid4().hex[:4]}", name="A", exchange="BIST", instrument_type=InstrumentType.STOCK)
        inst2 = Instrument(symbol=f"S2_{uuid.uuid4().hex[:4]}", name="B", exchange="BIST", instrument_type=InstrumentType.STOCK)
        db_session.add_all([inst1, inst2])

        p = Portfolio(user_id=user.id, name="Test P", portfolio_type="REAL")
        db_session.add(p)
        await db_session.commit()
        await db_session.refresh(p)
        p_id = p.id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        app.dependency_overrides[get_current_user] = override_get_current_user

        # 1. No portfolio
        res = await client.get("/api/v1/opportunities/")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 2
        # Check sorting: missing_data is probably true for these new ones, so raw_score matters less, but symbol ASC tie-breaker

        # 2. With portfolio
        res2 = await client.get(f"/api/v1/opportunities/?portfolio_id={p_id}")
        assert res2.status_code == 200
        data2 = res2.json()
        # Ensure user_fit logic ran (even if missing_data fallback triggered)
        assert "user_fit_score" in data2[0]

        # 3. IDOR test portfolio
        res_idor = await client.get("/api/v1/opportunities/?portfolio_id=9999999")
        assert res_idor.status_code == 404
