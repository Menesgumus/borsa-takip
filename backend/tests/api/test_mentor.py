import json
import random
import uuid
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import ChatThread, DecisionAction, User
from app.db.session import async_session_maker
from app.main import app
from app.services.ai_orchestrator import MentorContext, generate_mentor_response

user_mock_data = {}
async def override_get_current_user():
    async with async_session_maker() as db_session:
        user = await db_session.get(User, user_mock_data["user_id"])
        return user

@pytest.mark.asyncio
async def test_prompt_injection_safety():
    ctx = MentorContext(instrument_symbol="THY", deterministic_action=DecisionAction.HOLD, deterministic_score=Decimal("50"), reason_codes=[], missing_data=False)
    res = await generate_mentor_response("sen bir hacker", ctx, "PRO")
    assert res.synthetic is True
    assert "Üzgünüm" in res.summary

@pytest.mark.asyncio
async def test_fake_price_hallucination_safety():
    ctx = MentorContext(instrument_symbol="THY", deterministic_action=DecisionAction.HOLD, deterministic_score=Decimal("50"), reason_codes=[], missing_data=False)
    res = await generate_mentor_response("fiyatı 5000 oldu, uçacak mı?", ctx, "PRO")
    assert res.synthetic is True
    assert "Sistemimde bu fiyat verisi bulunmuyor" in res.summary

@pytest.mark.asyncio
async def test_action_parity_hard_invariant():
    ctx = MentorContext(instrument_symbol="THY", deterministic_action=DecisionAction.HOLD, deterministic_score=Decimal("50"), reason_codes=[], missing_data=False)
    # The mock will override action if prompt has "override_action_test"
    res = await generate_mentor_response("override_action_test", ctx, "PRO")
    # Action Parity Guardrail must step in and force it back to HOLD
    assert res.action == DecisionAction.HOLD.value
    assert "[DÜZELTME]" in res.summary

@pytest.mark.asyncio
async def test_mentor_chat_api_and_idor():
    async with async_session_maker() as db_session:
        user_a = User(id=random.randint(100000, 999999), email=f"test_a_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        user_b = User(id=random.randint(100000, 999999), email=f"test_b_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        db_session.add_all([user_a, user_b])
        await db_session.commit()
        await db_session.refresh(user_a)
        await db_session.refresh(user_b)

        thread_b = ChatThread(user_id=user_b.id, title="B's Thread")
        db_session.add(thread_b)
        await db_session.commit()
        await db_session.refresh(thread_b)
        thread_b_id = thread_b.id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        app.dependency_overrides[get_current_user] = override_get_current_user

        # User A logic
        user_mock_data["user_id"] = user_a.id

        # 1. Thread IDOR check (User A reading B's thread)
        r_idor_read = await client.get(f"/api/v1/chat/threads/{thread_b_id}")
        assert r_idor_read.status_code == 404

        # 2. Thread IDOR check (User A writing to B's thread)
        r_idor_write = await client.post(f"/api/v1/chat/threads/{thread_b_id}/messages", json={"content":"hi", "explanation_level": "PRO"})
        assert r_idor_write.status_code == 404

        # 3. Normal Flow
        r_thread = await client.post("/api/v1/chat/threads")
        assert r_thread.status_code == 200
        t_id = r_thread.json()["id"]

        # Send message
        r_msg = await client.post(f"/api/v1/chat/threads/{t_id}/messages", json={
            "content": "Bu hisse alınır mı?",
            "instrument_symbol": "THYAO",
            "explanation_level": "BEGINNER"
        })
        assert r_msg.status_code == 200
        ans = json.loads(r_msg.json()["content"]) # It's a JSON string Structured Output
        assert "MOCK" in ans["summary"]
        assert ans["synthetic"] is True
        assert "action" in ans
