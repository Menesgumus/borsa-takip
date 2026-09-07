import random
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import DecisionSnapshot, Instrument, InstrumentType, StrategyVersion, User
from app.db.session import async_session_maker
from app.main import app
from app.services.outcome_tracker import evaluate_strategy_versions

user_mock_data = {}
async def override_get_current_user():
    async with async_session_maker() as db_session:
        user = await db_session.get(User, user_mock_data["user_id"])
        return user

@pytest.mark.asyncio
async def test_outcome_tracking_api():
    async with async_session_maker() as db_session:
        user = User(id=random.randint(100000, 999999), email=f"outc_{uuid.uuid4()}@a.com", password_hash="pw", is_active=True)
        inst = Instrument(symbol=f"INST_{uuid.uuid4().hex[:4]}", name="Test", exchange="BIST", instrument_type=InstrumentType.STOCK)
        db_session.add_all([user, inst])
        await db_session.commit()
        await db_session.refresh(user)
        await db_session.refresh(inst)

        # Add snapshot
        snap = DecisionSnapshot(instrument_id=inst.id, action="BUY", score=0.8, engine_version="v1.0", reason_codes="TEST")
        db_session.add(snap)
        await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        app.dependency_overrides[get_current_user] = override_get_current_user
        user_mock_data["user_id"] = user.id

        r_trigger = await client.post("/api/v1/outcomes/trigger-tracker")
        assert r_trigger.status_code == 200

        r_recent = await client.get("/api/v1/outcomes/recent")
        assert r_recent.status_code == 200
        assert len(r_recent.json()) > 0

        # Cleanup
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_champion_challenger_no_auto_promotion():
    async with async_session_maker() as db_session:
        champ = StrategyVersion(name="DecEngine", version=f"1.0.{uuid.uuid4().hex[:6]}", status="CHAMPION", config_json="{}")
        chall = StrategyVersion(name="DecEngine", version=f"1.1.{uuid.uuid4().hex[:6]}", status="CHALLENGER", config_json="{}")
        db_session.add_all([champ, chall])
        await db_session.commit()

        # Trigger evaluate
        await evaluate_strategy_versions(db_session)

        # Verify challenger is NOT promoted automatically
        await db_session.refresh(chall)
        assert chall.status == "CHALLENGER"
        assert chall.promotion_reason == "BLOCKED_BY_DATA_VALIDATION"
