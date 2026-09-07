import pytest
from httpx import AsyncClient, ASGITransport
import uuid
import random
from decimal import Decimal

from app.main import app
from app.db.session import async_session_maker
from app.db.models import User, BehaviorProfile, TradeInsight
from app.api.v1.endpoints.auth import get_current_user

user_mock_data = {}
async def override_get_current_user():
    async with async_session_maker() as db_session:
        user = await db_session.get(User, user_mock_data["user_id"])
        return user

@pytest.mark.asyncio
async def test_behavior_profile_api():
    async with async_session_maker() as db_session:
        user = User(id=random.randint(100000, 999999), email=f"beh_{uuid.uuid4()}@a.com", password_hash="pw", is_active=True)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        app.dependency_overrides[get_current_user] = override_get_current_user
        user_mock_data["user_id"] = user.id
        
        # Test implicit creation
        r_prof = await client.get("/api/v1/behavior/profile")
        assert r_prof.status_code == 200
        assert r_prof.json()["fomo_tendency_score"] == '0.00'
        
        # Test insights empty
        r_ins = await client.get("/api/v1/behavior/insights")
        assert r_ins.status_code == 200
        assert r_ins.json() == []
