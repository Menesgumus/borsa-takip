import random
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import Instrument, InstrumentType, User
from app.db.session import async_session_maker
from app.main import app

user_mock_data = {}
async def override_get_current_user():
    async with async_session_maker() as db_session:
        user = await db_session.get(User, user_mock_data["user_id"])
        return user

@pytest.mark.asyncio
async def test_get_instrument_decision():
    async with async_session_maker() as db_session:
        user = User(id=random.randint(100000, 999999), email=f"test_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        db_session.add(user)
        inst = Instrument(id=random.randint(100000, 999999), symbol=f"TEST_{uuid.uuid4().hex[:4]}", name="Test", exchange="BIST", instrument_type=InstrumentType.STOCK)
        db_session.add(inst)
        await db_session.commit()
        await db_session.refresh(user)
        await db_session.refresh(inst)
        user_mock_data["user_id"] = user.id
        symbol = inst.symbol

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        app.dependency_overrides[get_current_user] = override_get_current_user

        # Market only
        res = await client.get(f"/api/v1/instruments/{symbol}/decision")
        assert res.status_code == 200
        data = res.json()
        assert "overall_market_score" in data
        assert data["market_view"] == "HOLD"
        assert data.get("decision_state") == "INSUFFICIENT_DATA"
        assert data["personal_action"] is None

        # Try with a mocked portfolio_id
        res2 = await client.post("/api/v1/portfolios", json={"name": "P1", "portfolio_type": "REAL"})
        p_id = res2.json()["id"]

        res_pers = await client.get(f"/api/v1/instruments/{symbol}/decision?portfolio_id={p_id}")
        assert res_pers.status_code == 200
        p_data = res_pers.json()
        # Portfolio Fit is returned
        assert p_data["portfolio_fit_score"] is not None
        assert p_data["personal_action"] == "HOLD"
