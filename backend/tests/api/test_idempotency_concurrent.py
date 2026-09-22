import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
import random
import uuid
from decimal import Decimal
from sqlalchemy.future import select

from app.main import app
from app.db.session import async_session_maker
from app.db.models import User, Instrument, PortfolioTransaction, IdempotencyRecord, InstrumentType
from app.api.v1.endpoints.auth import get_current_user

user_mock_data = {"user_id": 1}
async def override_get_current_user():
    return User(id=user_mock_data["user_id"], email="idemp@example.com", is_active=True)

@pytest.mark.asyncio
async def test_idempotency_concurrency():
    async with async_session_maker() as db_session:
        user = User(id=random.randint(100000, 999999), email=f"idemp_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
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
        
        # Create portfolio
        res = await client.post("/api/v1/portfolios", json={"name": "Idemp Test", "portfolio_type": "REAL"})
        p_id = res.json()["id"]

        # Deposit first to have cash
        await client.post(f"/api/v1/portfolios/{p_id}/transactions", json={"transaction_type": "DEPOSIT", "quantity": "10000"})

        # Concurrent requests
        idempotency_key = f"key_{uuid.uuid4()}"
        payload = {
            "side": "BUY",
            "instrument_id": inst_id,
            "quantity": "10",
            "native_execution_price": "100",
            "fee": "0"
        }
        headers = {"x-idempotency-key": idempotency_key}

        # Fire two requests concurrently
        coro1 = client.post(f"/api/v1/portfolios/{p_id}/manual-trade", json=payload, headers=headers)
        coro2 = client.post(f"/api/v1/portfolios/{p_id}/manual-trade", json=payload, headers=headers)
        
        res1, res2 = await asyncio.gather(coro1, coro2)
        
        # Both should succeed and return the exact same transaction
        assert res1.status_code == 200, f"res1: {res1.json()}"
        assert res2.status_code == 200, f"res2: {res2.json()}"
        assert res2.status_code == 200
        assert res1.json()["id"] == res2.json()["id"]
        
        # Verify exactly 1 idempotency record and 1 transaction was created
        async with async_session_maker() as db_verify:
            idemp_res = await db_verify.execute(select(IdempotencyRecord).where(IdempotencyRecord.idempotency_key == idempotency_key))
            idemp_records = idemp_res.scalars().all()
            assert len(idemp_records) == 1
            
            # The DEPOSIT is 1 transaction, the BUY should be exactly 1 transaction. Total = 2
            tx_res = await db_verify.execute(select(PortfolioTransaction).where(PortfolioTransaction.portfolio_id == p_id))
            tx_records = tx_res.scalars().all()
            assert len(tx_records) == 2

        # 1. Same user, same key, same family, different portfolio -> allowed
        res_p2 = await client.post("/api/v1/portfolios", json={"name": "Idemp Test 2", "portfolio_type": "REAL"})
        p_id2 = res_p2.json()["id"]
        await client.post(f"/api/v1/portfolios/{p_id2}/transactions", json={"transaction_type": "DEPOSIT", "quantity": "10000"})
        
        # Fire request with same idempotency key but on p_id2
        res_diff_port = await client.post(f"/api/v1/portfolios/{p_id2}/manual-trade", json=payload, headers=headers)
        assert res_diff_port.status_code == 200
        # Should be a DIFFERENT transaction
        assert res_diff_port.json()["id"] != res1.json()["id"]

        # 2. Same user, same portfolio, same family, same key, DIFFERENT canonical payload -> 409 Conflict
        payload_different = dict(payload)
        payload_different["quantity"] = "20"
        res_conflict = await client.post(f"/api/v1/portfolios/{p_id}/manual-trade", json=payload_different, headers=headers)
        assert res_conflict.status_code == 409
