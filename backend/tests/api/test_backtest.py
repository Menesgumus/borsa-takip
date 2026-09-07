import datetime
import random
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import BacktestJob, BacktestResult, User
from app.db.session import async_session_maker
from app.main import app
from app.services.backtest import run_backtest_job

user_mock_data = {}
async def override_get_current_user():
    async with async_session_maker() as db_session:
        user = await db_session.get(User, user_mock_data["user_id"])
        return user

@pytest.mark.asyncio
async def test_backtest_service_engine():
    async with async_session_maker() as db_session:
        user = User(id=random.randint(100000, 999999), email=f"bt_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        job = BacktestJob(
            user_id=user.id,
            strategy_name="DecisionEngineV1",
            strategy_version="1.0.0",
            start_date=datetime.datetime(2023, 1, 1, tzinfo=datetime.UTC),
            end_date=datetime.datetime(2023, 1, 31, tzinfo=datetime.UTC),
            initial_capital=100000.0,
            commission_pct=0.001,
            slippage_pct=0.0005
        )
        db_session.add(job)
        await db_session.commit()
        from sqlalchemy.future import select
        from sqlalchemy.orm import selectinload
        res_job = await db_session.execute(select(BacktestJob).options(selectinload(BacktestJob.result)).where(BacktestJob.id == job.id))
        job = res_job.scalars().first()

        # Run worker
        await run_backtest_job(db_session, job.id)

        # Check result
        from sqlalchemy.future import select
        from sqlalchemy.orm import selectinload
        res_job = await db_session.execute(select(BacktestJob).options(selectinload(BacktestJob.result)).where(BacktestJob.id == job.id))
        job = res_job.scalars().first()
        assert job.status == "COMPLETED"
        res_real = await db_session.execute(select(BacktestResult).where(BacktestResult.job_id == job.id))
        actual_result = res_real.scalars().first()
        assert actual_result is not None
        assert "PASS" in actual_result.bias_audit # Check explicit bias audit requirement
        assert "UNVERIFIED" in actual_result.bias_audit
        assert actual_result.validation_state == "LIMITED"

@pytest.mark.asyncio
async def test_backtest_api_idor():
    async with async_session_maker() as db_session:
        user_a = User(id=random.randint(100000, 999999), email=f"bt_a_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        user_b = User(id=random.randint(100000, 999999), email=f"bt_b_{uuid.uuid4()}@example.com", password_hash="pw", is_active=True)
        db_session.add_all([user_a, user_b])
        await db_session.commit()
        await db_session.refresh(user_a)
        await db_session.refresh(user_b)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        app.dependency_overrides[get_current_user] = override_get_current_user

        user_mock_data["user_id"] = user_a.id

        # Create
        r_create = await client.post("/api/v1/backtests/", json={
            "strategy_name": "TestStrat",
            "strategy_version": "1.0",
            "start_date": "2023-01-01T00:00:00Z",
            "end_date": "2023-01-31T00:00:00Z",
            "initial_capital": 10000.0
        })
        assert r_create.status_code == 200
        job_id = r_create.json()["id"]

        # IDOR switch
        user_mock_data["user_id"] = user_b.id
        r_get = await client.get(f"/api/v1/backtests/{job_id}")
        assert r_get.status_code == 404

        r_get_res = await client.get(f"/api/v1/backtests/{job_id}/result")
        assert r_get_res.status_code == 404
