import random
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import EducationalLesson, EducationalModule, User
from app.db.session import async_session_maker
from app.main import app

user_mock_data = {}
async def override_get_current_user():
    async with async_session_maker() as db_session:
        user = await db_session.get(User, user_mock_data["user_id"])
        return user

@pytest.mark.asyncio
async def test_education_api():
    async with async_session_maker() as db_session:
        user_a = User(id=random.randint(100000, 999999), email=f"test_edu_a_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        user_b = User(id=random.randint(100000, 999999), email=f"test_edu_b_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        mod = EducationalModule(slug=f"test-mod-{uuid.uuid4().hex[:4]}", title="T", description="D", category="FUNDAMENTALS", display_order=1)
        db_session.add_all([user_a, user_b, mod])
        await db_session.commit()
        await db_session.refresh(mod)
        les = EducationalLesson(module_id=mod.id, slug=f"test-les-{uuid.uuid4().hex[:4]}", title="L1", content_beginner="C", content_detailed="D", display_order=1, estimated_minutes=5)
        db_session.add(les)
        await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        app.dependency_overrides[get_current_user] = override_get_current_user
        user_mock_data["user_id"] = user_a.id

        # 1. Get modules
        r_mod = await client.get("/api/v1/education/modules")
        assert r_mod.status_code == 200
        modules = r_mod.json()
        assert len(modules) > 0
        lesson_id = modules[0]["lessons"][0]["id"]

        # 2. Update Progress
        r_prog = await client.put(f"/api/v1/education/lessons/{lesson_id}/progress", json={"is_completed": True, "last_position": "end"})
        assert r_prog.status_code == 200

        # 3. Check Progress was saved
        r_mod2 = await client.get("/api/v1/education/modules")
        m2 = r_mod2.json()
        completed_lesson = [l for m in m2 for l in m["lessons"] if l["id"] == lesson_id][0]
        assert completed_lesson["is_completed"] is True

        # 4. IDOR Check: Switch to User B
        user_mock_data["user_id"] = user_b.id
        r_mod_b = await client.get("/api/v1/education/modules")
        m_b = r_mod_b.json()
        lesson_b = [l for m in m_b for l in m["lessons"] if l["id"] == lesson_id][0]
        assert lesson_b["is_completed"] is False
