import json
import random

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.endpoints.auth import get_current_user
from app.core.redis import redis_client
from app.db.models import AssetClass, Instrument, Portfolio, User, UserProfile
from app.db.session import async_session_maker
from app.main import app
from app.services.scanner import scan_opportunities


@pytest.fixture
async def setup_test_user_and_portfolio():
    async with async_session_maker() as db:
        user = User(
            email=f"test{random.randint(1000, 9999)}@example.com",
            password_hash="mock"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        prof = UserProfile(user_id=user.id)
        db.add(prof)
        await db.commit()

        port = Portfolio(
            user_id=user.id,
            name="Test Port",
            currency="TRY"
        )
        db.add(port)
        await db.commit()
        await db.refresh(port)

        return user, port

@pytest.mark.asyncio
async def test_opportunity_asset_class_filter_before_limit(setup_test_user_and_portfolio):
    user, port = setup_test_user_and_portfolio

    app.dependency_overrides[get_current_user] = lambda: user

    async with async_session_maker() as db:
        # Create many BIST items that would outrank GOLD if limit is small
        rand_suffix = random.randint(10000, 99999)
        bist_instruments = []
        for i in range(25):
            inst = Instrument(
                symbol=f"BIST{rand_suffix}_{i}",
                name=f"Bist {i}",
                exchange="BIST",
                asset_class=AssetClass.BIST_EQUITY,
                currency="TRY",
                is_active=True
            )
            db.add(inst)
            bist_instruments.append(inst)

        gold_inst = Instrument(
            symbol=f"QAGOLD_{rand_suffix}",
            name="QA Gold",
            exchange="QA",
            asset_class=AssetClass.GOLD,
            currency="TRY",
            is_active=True
        )
        db.add(gold_inst)

        fx_inst = Instrument(
            symbol=f"QAFX_{rand_suffix}",
            name="QA FX",
            exchange="QA",
            asset_class=AssetClass.FX_REFERENCE,
            currency="TRY",
            is_active=True
        )
        db.add(fx_inst)

        await db.commit()
        await db.refresh(gold_inst)
        for i in bist_instruments: await db.refresh(i)

        # Mock the Redis market cache so scan_opportunities thinks these are all ranked
        market_results = {}
        for i, inst in enumerate(bist_instruments):
            market_results[str(inst.id)] = {
                "symbol": inst.symbol,
                "quote_price": "100.0",
                "quote_data_state": "LIVE",
                "quote_as_of": "2026-01-01T00:00:00+00:00",
                "market_score": str(90.0 - i), # BIST get high scores (90 to 65)
                "data_quality_score": "100",
                "technical_score": "90",
                "fundamental_score": "90",
                "news_score": "90",
                "risk_reward_score": "90",
                "market_view": "BUY",
                "reason_codes": [],
                "warnings": [],
                "missing_data": False,
                "decision_state": "COMPLETE",
                "engine_version": "v5"
            }

        # Gold gets lower score
        market_results[str(gold_inst.id)] = {
                "symbol": gold_inst.symbol,
                "quote_price": "2000.0",
                "quote_data_state": "LIVE",
                "quote_as_of": "2026-01-01T00:00:00+00:00",
                "market_score": "50.0",
                "data_quality_score": "100",
                "technical_score": "50",
                "fundamental_score": None,
                "news_score": "50",
                "risk_reward_score": "50",
                "market_view": "HOLD",
                "reason_codes": [],
                "warnings": [],
                "missing_data": False,
                "decision_state": "COMPLETE",
                "engine_version": "v5"
        }

        # FX gets very high score just in case, but it's FX
        market_results[str(fx_inst.id)] = {
                "symbol": fx_inst.symbol,
                "quote_price": "30.0",
                "quote_data_state": "LIVE",
                "quote_as_of": "2026-01-01T00:00:00+00:00",
                "market_score": "99.0",
                "data_quality_score": "100",
                "technical_score": "99",
                "fundamental_score": None,
                "news_score": "99",
                "risk_reward_score": "99",
                "market_view": "BUY",
                "reason_codes": [],
                "warnings": [],
                "missing_data": False,
                "decision_state": "COMPLETE",
                "engine_version": "v5"
        }

        if redis_client:
            from app.services.decision_engine import ENGINE_VERSION
            cache_key = f"opportunities:market:v5:MEDIUM:{ENGINE_VERSION}"
            await redis_client.set(cache_key, json.dumps(market_results))

    # Test the backend function directly
    async with async_session_maker() as db:
        res_gold = await scan_opportunities(db, user=user, limit=5, asset_class=AssetClass.GOLD)
        assert len(res_gold) >= 1
        assert res_gold[0].asset_class == "GOLD"

        res_bist = await scan_opportunities(db, user=user, limit=5, asset_class=AssetClass.BIST_EQUITY)
        assert len(res_bist) == 5
        assert all(r.asset_class == "BIST_EQUITY" for r in res_bist)

        res_all = await scan_opportunities(db, user=user, limit=10)
        assert all(r.asset_class != "FX_REFERENCE" for r in res_all)

    # Test API endpoint
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/v1/opportunities?limit=5&asset_class=GOLD")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1

        resp2 = await async_client.get("/api/v1/opportunities?limit=5&asset_class=BIST_EQUITY")
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert len(data2) == 5

        resp3 = await ac.get("/api/v1/opportunities?limit=10")
        assert resp3.status_code == 200
        data3 = resp3.json()
        assert not any(r["asset_class"] == "FX_REFERENCE" for r in data3)

        resp4 = await ac.get("/api/v1/opportunities?limit=10&asset_class=INVALID_CLASS")
        assert resp4.status_code == 422

        resp5 = await ac.get("/api/v1/opportunities?limit=10&asset_class=FX_REFERENCE")
        assert resp5.status_code == 422

    app.dependency_overrides.pop(get_current_user, None)
import pytest

from httpx import AsyncClient

from sqlalchemy import select



from app.db.models import Instrument, Portfolio

from app.db.session import async_session_maker

from app.api.v1.endpoints.auth import get_current_user

from app.main import app

from app.core.redis import redis_client



@pytest.fixture

async def cold_cache_setup(setup_test_user_and_portfolio):

    user, port = setup_test_user_and_portfolio

    app.dependency_overrides[get_current_user] = lambda: user

    

    # Ensure Redis is flushed

    await redis_client.flushdb()

    

    yield user, port

    

    app.dependency_overrides.pop(get_current_user, None)



@pytest.mark.asyncio

async def test_opportunities_cold_cache_handles_gracefully(cold_cache_setup, async_client):

    user, port = cold_cache_setup

    

    # First request: Cache is empty

    resp1 = await async_client.get(f"/api/v1/opportunities?portfolio_id={port.id}&asset_class=BIST_EQUITY&limit=20")

    assert resp1.status_code == 200, f"Cold cache failed: {resp1.text}"

    

    data1 = resp1.json()

    assert isinstance(data1, list)

    

    # Second request: Cache is warm

    resp2 = await async_client.get(f"/api/v1/opportunities?portfolio_id={port.id}&asset_class=BIST_EQUITY&limit=20")

    assert resp2.status_code == 200, f"Warm cache failed: {resp2.text}"

    

    data2 = resp2.json()

    assert len(data1) == len(data2)




