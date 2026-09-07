import random
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import Instrument, InstrumentType, User
from app.db.session import async_session_maker
from app.main import app

# Mock auth dynamically
user_mock_data = {"user1_id": 1, "user2_id": 2}

async def override_get_current_user():
    return User(id=user_mock_data["user1_id"], email="test1@example.com")

async def override_get_current_user2():
    return User(id=user_mock_data["user2_id"], email="test2@example.com")

@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_portfolio_lifecycle_and_accounting():
    async with async_session_maker() as db_session:
        user = User(id=random.randint(100000, 999999), email=f"test_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        db_session.add(user)
        inst = Instrument(id=random.randint(100000, 999999), symbol=f"TEST_{uuid.uuid4().hex[:4]}", name="Test", exchange="BIST", instrument_type=InstrumentType.STOCK)
        db_session.add(inst)
        await db_session.commit()
        await db_session.refresh(user)
        await db_session.refresh(inst)
        user_mock_data["user1_id"] = user.id
        inst_id = inst.id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/v1/portfolios/", json={"name": "My Paper", "portfolio_type": "PAPER"})
        assert res.status_code == 200
        p_id = res.json()["id"]

        # 2. Buy before deposit -> reject
        res = await client.post(f"/api/v1/portfolios/{p_id}/transactions", json={
            "transaction_type": "BUY",
            "instrument_id": inst_id,
            "quantity": "10",
            "price": "100"
        })
        assert res.status_code == 400

        # 3. Deposit
        res = await client.post(f"/api/v1/portfolios/{p_id}/transactions", json={
            "transaction_type": "DEPOSIT",
            "quantity": "10000"
        })
        assert res.status_code == 200

        # 4. Buy
        res = await client.post(f"/api/v1/portfolios/{p_id}/transactions", json={
            "transaction_type": "BUY",
            "instrument_id": inst_id,
            "quantity": "10",
            "price": "100",
            "fee": "10"
        })
        assert res.status_code == 200

        # 5. Sell part
        res = await client.post(f"/api/v1/portfolios/{p_id}/transactions", json={
            "transaction_type": "SELL",
            "instrument_id": inst_id,
            "quantity": "4",
            "price": "150",
            "fee": "5"
        })
        assert res.status_code == 200

        # 6. Summary
        res = await client.get(f"/api/v1/portfolios/{p_id}/summary")
        assert res.status_code == 200
        data = res.json()
        assert float(data["cash_balance"]) == 9585.0
        assert len(data["positions"]) == 1
        pos = data["positions"][0]
        assert float(pos["quantity"]) == 6.0
        assert float(pos["average_cost"]) == 101.0
        assert float(pos["realized_pnl"]) == 191.0

@pytest.mark.asyncio
async def test_portfolio_idor():
    async with async_session_maker() as db_session:
        user1 = User(id=random.randint(100000, 999999), email=f"test_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        user2 = User(id=random.randint(100000, 999999), email=f"test_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        db_session.add(user1)
        db_session.add(user2)
        await db_session.commit()
        await db_session.refresh(user1)
        await db_session.refresh(user2)
        user_mock_data["user1_id"] = user1.id
        user_mock_data["user2_id"] = user2.id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        app.dependency_overrides[get_current_user] = override_get_current_user
        res = await client.post("/api/v1/portfolios/", json={"name": "My Paper IDOR", "portfolio_type": "PAPER"})
        p_id = res.json()["id"]

        app.dependency_overrides[get_current_user] = override_get_current_user2
        res = await client.get(f"/api/v1/portfolios/{p_id}/summary")
        assert res.status_code == 404

        res = await client.post(f"/api/v1/portfolios/{p_id}/transactions", json={
            "transaction_type": "DEPOSIT",
            "quantity": "1000"
        })
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_portfolio_journal():
    async with async_session_maker() as db_session:
        user = User(id=random.randint(100000, 999999), email=f"test_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        user_mock_data["user1_id"] = user.id
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        app.dependency_overrides[get_current_user] = override_get_current_user
        res = await client.post("/api/v1/portfolios/", json={"name": "Journal Test", "portfolio_type": "REAL"})
        p_id = res.json()["id"]
        
        # Add Journal
        res = await client.post(f"/api/v1/portfolios/{p_id}/journals", json={
            "setup": "Breakout",
            "reason": "MACD cross",
            "emotion": "Confident"
        })
        assert res.status_code == 200
        
        # Verify it didn't mutate financial ledger
        res = await client.get(f"/api/v1/portfolios/{p_id}/summary")
        assert res.status_code == 200
        assert float(res.json()["cash_balance"]) == 0.0
        
        # IDOR check
        app.dependency_overrides[get_current_user] = override_get_current_user2
        res = await client.post(f"/api/v1/portfolios/{p_id}/journals", json={
            "setup": "Hacked"
        })
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_portfolio_risk_and_whatif():
    async with async_session_maker() as db_session:
        user = User(id=random.randint(100000, 999999), email=f"test_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        db_session.add(user)
        inst = Instrument(id=random.randint(100000, 999999), symbol=f"TEST_{uuid.uuid4().hex[:4]}", name="Test", exchange="BIST", instrument_type=InstrumentType.STOCK)
        db_session.add(inst)
        await db_session.commit()
        await db_session.refresh(user)
        await db_session.refresh(inst)
        user_mock_data["user1_id"] = user.id
        inst_id = inst.id
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        app.dependency_overrides[get_current_user] = override_get_current_user
        res = await client.post("/api/v1/portfolios/", json={"name": "Risk Test", "portfolio_type": "REAL"})
        p_id = res.json()["id"]
        
        await client.post(f"/api/v1/portfolios/{p_id}/transactions", json={
            "transaction_type": "DEPOSIT",
            "quantity": "10000"
        })
        
        await client.post(f"/api/v1/portfolios/{p_id}/transactions", json={
            "transaction_type": "BUY",
            "instrument_id": inst_id,
            "quantity": "10",
            "price": "100"
        })
        
        # Risk Check
        res = await client.get(f"/api/v1/portfolios/{p_id}/risk")
        assert res.status_code == 200
        risk = res.json()
        assert risk["data_freshness"] == "STALE" # No prices seeded
        assert float(risk["cash_exposure"]) == 9000.0
        
        # What-If causing insufficient cash
        res = await client.post(f"/api/v1/portfolios/{p_id}/what-if", json={
            "transaction_type": "BUY",
            "instrument_id": inst_id,
            "quantity": "100",
            "price": "100"
        })
        assert res.status_code == 400
        
        # What-If valid buy
        res = await client.post(f"/api/v1/portfolios/{p_id}/what-if", json={
            "transaction_type": "BUY",
            "instrument_id": inst_id,
            "quantity": "10",
            "price": "100"
        })
        assert res.status_code == 200
        delta = res.json()
        assert "before_risk" in delta
        assert "after_risk" in delta
        
        # Verify What-If didn't mutate ledger
        res = await client.get(f"/api/v1/portfolios/{p_id}/risk")
        assert float(res.json()["cash_exposure"]) == 9000.0
