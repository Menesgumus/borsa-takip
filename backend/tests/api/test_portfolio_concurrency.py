import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
import random
import uuid
from sqlalchemy.future import select

from app.main import app
from app.db.session import async_session_maker
from app.db.models import User, Instrument, PortfolioTransaction, InstrumentType
from app.api.v1.endpoints.auth import get_current_user

user_mock_data = {"user_id": 1}
async def override_get_current_user():
    return User(id=user_mock_data["user_id"], email="mut@example.com", is_active=True)

@pytest.mark.asyncio
async def test_portfolio_mutation_concurrency():
    async with async_session_maker() as db_session:
        user = User(id=random.randint(100000, 999999), email=f"mut_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        inst = Instrument(id=random.randint(100000, 999999), symbol=f"TEST_{uuid.uuid4().hex[:4]}", name="Test", exchange="BIST", instrument_type=InstrumentType.STOCK)
        db_session.add(user)
        db_session.add(inst)
        await db_session.commit()
        await db_session.refresh(user)
        await db_session.refresh(inst)
        user_id = user.id
        inst_id = inst.id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        app.dependency_overrides[get_current_user] = override_get_current_user
        user_mock_data["user_id"] = user_id
        
        # 1. Oversell test
        res = await client.post("/api/v1/portfolios", json={"name": "Oversell Test", "portfolio_type": "REAL"})
        p_id = res.json()["id"]
        
        await client.post(f"/api/v1/portfolios/{p_id}/transactions", json={"transaction_type": "DEPOSIT", "quantity": "10000"})
        await client.post(f"/api/v1/portfolios/{p_id}/manual-trade", json={"side": "BUY", "instrument_id": inst_id, "quantity": "10", "native_execution_price": "100", "fee": "0"})
        
        coro1 = client.post(f"/api/v1/portfolios/{p_id}/manual-trade", json={"side": "SELL", "instrument_id": inst_id, "quantity": "7", "native_execution_price": "100", "fee": "0"})
        coro2 = client.post(f"/api/v1/portfolios/{p_id}/manual-trade", json={"side": "SELL", "instrument_id": inst_id, "quantity": "7", "native_execution_price": "100", "fee": "0"})
        r1, r2 = await asyncio.gather(coro1, coro2)
        
        statuses = [r1.status_code, r2.status_code]
        assert 200 in statuses
        assert 400 in statuses
        
        # 2. Double-spend BUY
        res = await client.post("/api/v1/portfolios", json={"name": "Double Spend Test", "portfolio_type": "REAL"})
        p_id2 = res.json()["id"]
        await client.post(f"/api/v1/portfolios/{p_id2}/transactions", json={"transaction_type": "DEPOSIT", "quantity": "1000"})
        
        coro3 = client.post(f"/api/v1/portfolios/{p_id2}/manual-trade", json={"side": "BUY", "instrument_id": inst_id, "quantity": "6", "native_execution_price": "100", "fee": "0"}) # 6 * 100 = 600
        coro4 = client.post(f"/api/v1/portfolios/{p_id2}/manual-trade", json={"side": "BUY", "instrument_id": inst_id, "quantity": "6", "native_execution_price": "100", "fee": "0"})
        r3, r4 = await asyncio.gather(coro3, coro4)
        
        statuses = [r3.status_code, r4.status_code]
        assert 200 in statuses
        assert 400 in statuses
        
        # 3. Concurrent withdrawal
        res = await client.post("/api/v1/portfolios", json={"name": "Withdrawal Test", "portfolio_type": "REAL"})
        p_id3 = res.json()["id"]
        await client.post(f"/api/v1/portfolios/{p_id3}/transactions", json={"transaction_type": "DEPOSIT", "quantity": "100"})
        
        coro5 = client.post(f"/api/v1/portfolios/{p_id3}/transactions", json={"transaction_type": "WITHDRAWAL", "quantity": "60"})
        coro6 = client.post(f"/api/v1/portfolios/{p_id3}/transactions", json={"transaction_type": "WITHDRAWAL", "quantity": "60"})
        r5, r6 = await asyncio.gather(coro5, coro6)
        
        statuses = [r5.status_code, r6.status_code]
        assert 200 in statuses
        assert 400 in statuses
