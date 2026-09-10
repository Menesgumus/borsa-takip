import random
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import User
from app.db.session import async_session_maker
from app.main import app

user_mock_data = {}
async def override_get_current_user():
    async with async_session_maker() as db_session:
        user = await db_session.get(User, user_mock_data["user_id"])
        return user


@pytest.mark.asyncio
async def test_mentor_chat_api_is_gone():
    async with async_session_maker() as db_session:
        user_a = User(id=random.randint(100000, 999999), email=f"test_a_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        db_session.add(user_a)
        await db_session.commit()
        user_mock_data["user_id"] = user_a.id

    app.dependency_overrides[get_current_user] = override_get_current_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Test that chat threads endpoint returns 410
        r_thread = await client.post("/api/v1/chat/threads")
        assert r_thread.status_code == 410

        # Test that message endpoint returns 410
        r_msg = await client.post("/api/v1/chat/threads/1/messages", json={
            "content": "Test"
        })
        assert r_msg.status_code == 410

        # Test get thread endpoint returns 410
        r_get = await client.get("/api/v1/chat/threads/1")
        assert r_get.status_code == 410

    app.dependency_overrides.clear()
