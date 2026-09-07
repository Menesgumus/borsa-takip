import pytest
from httpx import AsyncClient, ASGITransport
import uuid
import random
from decimal import Decimal

from app.main import app
from app.db.session import async_session_maker
from app.db.models import User, AlertRule, AlertType, Instrument, InstrumentType
from app.api.v1.endpoints.auth import get_current_user
from app.services.alerts import evaluate_alert

user_mock_data = {}
async def override_get_current_user():
    async with async_session_maker() as db_session:
        user = await db_session.get(User, user_mock_data["user_id"])
        return user

@pytest.mark.asyncio
async def test_alerts_service_cooldown():
    async with async_session_maker() as db_session:
        user = User(id=random.randint(100000, 999999), email=f"alert_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        db_session.add(user)
        inst = Instrument(symbol=f"TEST_{uuid.uuid4().hex[:4]}", name="A", exchange="BIST", instrument_type=InstrumentType.STOCK)
        db_session.add(inst)
        await db_session.commit()
        await db_session.refresh(user)
        await db_session.refresh(inst)
        
        rule = AlertRule(user_id=user.id, alert_type=AlertType.PRICE, instrument_id=inst.id, operator=">", threshold=Decimal("100"), cooldown_minutes=60)
        db_session.add(rule)
        await db_session.commit()
        await db_session.refresh(rule)
        
        # 1. Trigger initially
        triggered1 = await evaluate_alert(db_session, rule, current_value=150.0, context_data={"message": "Fiyat 100'ü aştı"})
        assert triggered1 is True
        
        # 2. Trigger again immediately (should fail due to cooldown)
        await db_session.refresh(rule)
        triggered2 = await evaluate_alert(db_session, rule, current_value=160.0, context_data={"message": "Fiyat 100'ü aştı"})
        assert triggered2 is False

@pytest.mark.asyncio
async def test_alerts_api():
    async with async_session_maker() as db_session:
        user_a = User(id=random.randint(100000, 999999), email=f"test_a_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        user_b = User(id=random.randint(100000, 999999), email=f"test_b_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        db_session.add_all([user_a, user_b])
        await db_session.commit()
        await db_session.refresh(user_a)
        await db_session.refresh(user_b)
        
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        user_mock_data["user_id"] = user_a.id
        
        # Create rule
        r_create = await client.post("/api/v1/alerts/rules", json={
            "alert_type": "PRICE",
            "operator": "<",
            "threshold": 50,
            "cooldown_minutes": 120
        })
        assert r_create.status_code == 200
        data = r_create.json()
        assert data["alert_type"] == "PRICE"
        
        # List rules
        r_list = await client.get("/api/v1/alerts/rules")
        assert len(r_list.json()) == 1
        
        # IDOR check
        user_mock_data["user_id"] = user_b.id
        r_list_b = await client.get("/api/v1/alerts/rules")
        assert len(r_list_b.json()) == 0
