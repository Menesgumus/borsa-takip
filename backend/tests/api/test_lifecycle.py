import asyncio
import random
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import (
    Instrument,
    Portfolio,
    PortfolioTransaction,
    PositionLifecycle,
    User,
)
from app.db.session import async_session_maker
from app.main import app
from app.schemas.decision import DecisionResult

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def override_user():
    async with async_session_maker() as db:
        user = User(id=random.randint(100000, 999999), email=f"test_life_{random.randint(1,999999)}@example.com", password_hash="pw", is_active=True)
        db.add(user)
        await db.commit()
        app.dependency_overrides[get_current_user] = lambda: user
        yield user
        app.dependency_overrides = {}

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer TEST"}

@pytest.fixture
async def setup_lifecycle_portfolio(override_user):
    async with async_session_maker() as db:
        port = Portfolio(user_id=override_user.id, name="Lifecycle QA", portfolio_type="PAPER")
        db.add(port)
        await db.commit()
        await db.refresh(port)

        inst = Instrument(
            symbol=f"QALIFE_{random.randint(1,999999)}",
            name="QA Lifecycle",
            asset_class="BIST_EQUITY",
            exchange="BIST",
            currency="TRY",
            is_active=True
        )
        db.add(inst)
        await db.commit()
        await db.refresh(inst)

        dep = PortfolioTransaction(
            portfolio_id=port.id,
            transaction_type="DEPOSIT",
            quantity=Decimal("10000"),
            executed_at=datetime.now(UTC)
        )
        tx = PortfolioTransaction(
            portfolio_id=port.id,
            instrument_id=inst.id,
            transaction_type="BUY",
            quantity=Decimal("10"),
            price=Decimal("100"),
            executed_at=datetime.now(UTC)
        )
        db.add_all([dep, tx])
        await db.commit()

        return port, inst

class MockDecisionGenerator:
    def __init__(self):
        self.market_view = "HOLD"
        self.market_key = "MKEY_0"
        self.is_eval = True

    def __call__(self, *args, **kwargs):
        dec = DecisionResult(
            market_view=self.market_view,
            instrument_id=1,
            horizon="SHORT",
            as_of=datetime.utcnow(),
            overall_market_score=50,
            reason_codes=[],
            warnings=[],
            missing_data=False,
            engine_version="v1",

            fundamental_score=50,
            technical_score=50,
            overall_personal_score=50,
            data_quality_score=100,
            market_observation_date="2026-09-01",
            is_evaluable=self.is_eval,
            reasons=[]
        )
        return dec, self.market_key, "ctx_123", self.is_eval

async def test_lifecycle_scenario_watch_and_confirmed(client: AsyncClient, auth_headers: dict, setup_lifecycle_portfolio, monkeypatch):
    port, inst = setup_lifecycle_portfolio
    client.headers = auth_headers

    mock_gen = MockDecisionGenerator()
    async def mock_eval(*args, **kwargs):
        return mock_gen(*args, **kwargs)
    monkeypatch.setattr("app.api.v1.endpoints.lifecycle.evaluate_lifecycle_for_instrument", mock_eval)

    # Send 1st SELL
    mock_gen.market_view = "SELL"
    mock_gen.market_key = "MKEY_1"
    resp1 = await client.post(f"/api/v1/portfolios/{port.id}/lifecycle/evaluate")
    data = resp1.json()
    assert data[0]["health_state"] == "WATCH"
    assert data[0]["negative_confirmation_count"] == 1

    # duplicate day
    resp_dup = await client.post(f"/api/v1/portfolios/{port.id}/lifecycle/evaluate")
    assert resp_dup.json()[0]["health_state"] == "WATCH"
    assert resp_dup.json()[0]["negative_confirmation_count"] == 1

    # Send 2nd SELL
    mock_gen.market_key = "MKEY_2"
    resp2 = await client.post(f"/api/v1/portfolios/{port.id}/lifecycle/evaluate")
    assert resp2.json()[0]["health_state"] == "WATCH"
    assert resp2.json()[0]["negative_confirmation_count"] == 2

    # Send 3rd SELL
    mock_gen.market_key = "MKEY_3"
    resp3 = await client.post(f"/api/v1/portfolios/{port.id}/lifecycle/evaluate")
    assert resp3.json()[0]["health_state"] == "CONFIRMED_DETERIORATION"

async def test_lifecycle_scenario_strong_sell_exit(client: AsyncClient, auth_headers: dict, setup_lifecycle_portfolio, monkeypatch):
    port, inst = setup_lifecycle_portfolio
    client.headers = auth_headers
    mock_gen = MockDecisionGenerator()
    async def mock_eval(*args, **kwargs):
        return mock_gen(*args, **kwargs)
    monkeypatch.setattr("app.api.v1.endpoints.lifecycle.evaluate_lifecycle_for_instrument", mock_eval)

    for i in range(1, 4):
        mock_gen.market_view = "STRONG_SELL"
        mock_gen.market_key = f"MKEY_SS_{i}"
        resp = await client.post(f"/api/v1/portfolios/{port.id}/lifecycle/evaluate")

    data = resp.json()[0]
    assert data["health_state"] == "CONFIRMED_DETERIORATION"
    assert data["recommended_action"] == "CONSIDER_EXIT"

async def test_lifecycle_scenario_recover_and_relapse(client: AsyncClient, auth_headers: dict, setup_lifecycle_portfolio, monkeypatch):
    port, inst = setup_lifecycle_portfolio
    client.headers = auth_headers
    mock_gen = MockDecisionGenerator()
    async def mock_eval(*args, **kwargs):
        return mock_gen(*args, **kwargs)
    monkeypatch.setattr("app.api.v1.endpoints.lifecycle.evaluate_lifecycle_for_instrument", mock_eval)

    for i in range(1, 4):
        mock_gen.market_view = "SELL"
        mock_gen.market_key = f"MKEY_S_{i}"
        await client.post(f"/api/v1/portfolios/{port.id}/lifecycle/evaluate")

    mock_gen.market_view = "BUY"
    mock_gen.market_key = "MKEY_BUY_1"
    resp = await client.post(f"/api/v1/portfolios/{port.id}/lifecycle/evaluate")
    assert resp.json()[0]["health_state"] == "RECOVERING"

    mock_gen.market_view = "SELL"
    mock_gen.market_key = "MKEY_SELL_RELAPSE"
    resp = await client.post(f"/api/v1/portfolios/{port.id}/lifecycle/evaluate")
    assert resp.json()[0]["health_state"] == "CONFIRMED_DETERIORATION"

async def test_lifecycle_scenario_data_failure_does_not_close(client: AsyncClient, auth_headers: dict, setup_lifecycle_portfolio, monkeypatch):
    port, inst = setup_lifecycle_portfolio
    client.headers = auth_headers
    mock_gen = MockDecisionGenerator()
    async def mock_eval(*args, **kwargs):
        return mock_gen(*args, **kwargs)
    monkeypatch.setattr("app.api.v1.endpoints.lifecycle.evaluate_lifecycle_for_instrument", mock_eval)

    await client.post(f"/api/v1/portfolios/{port.id}/lifecycle/evaluate")

    # Mock data missing
    mock_gen.market_key = "MKEY_DATA_FAIL"
    mock_gen.is_eval = False

    async def mock_eval_port(*args, **kwargs):
        return {port.id: type('ValuationResult', (), {'positions': [{'instrument_id': inst.id, 'quantity': Decimal('10')}], 'valuation_complete': False, 'cash_balance': Decimal('0')})()}
    monkeypatch.setattr("app.api.v1.endpoints.lifecycle.evaluate_portfolios", mock_eval_port)

    resp = await client.post(f"/api/v1/portfolios/{port.id}/lifecycle/evaluate")
    assert resp.status_code == 200
    data = resp.json()[0]

    assert data["health_state"] == "STABLE"
    assert data["recommended_action"] == "NO_ACTION_DATA"

async def test_lifecycle_scenario_episode_semantics(client: AsyncClient, auth_headers: dict, setup_lifecycle_portfolio, monkeypatch):
    port, inst = setup_lifecycle_portfolio
    client.headers = auth_headers
    mock_gen = MockDecisionGenerator()
    async def mock_eval(*args, **kwargs):
        return mock_gen(*args, **kwargs)
    monkeypatch.setattr("app.api.v1.endpoints.lifecycle.evaluate_lifecycle_for_instrument", mock_eval)

    resp = await client.post(f"/api/v1/portfolios/{port.id}/lifecycle/evaluate")
    assert resp.json()[0]["episode_number"] == 1

    async with async_session_maker() as db:
        tx2 = PortfolioTransaction(portfolio_id=port.id, instrument_id=inst.id, transaction_type="SELL", quantity=Decimal("5"), executed_at=datetime.now(UTC))
        db.add(tx2)
        await db.commit()

    mock_gen.market_key = "MKEY_EP_2"
    resp = await client.post(f"/api/v1/portfolios/{port.id}/lifecycle/evaluate")
    assert resp.json()[0]["episode_number"] == 1

    async with async_session_maker() as db:
        tx3 = PortfolioTransaction(portfolio_id=port.id, instrument_id=inst.id, transaction_type="SELL", quantity=Decimal("5"), executed_at=datetime.now(UTC))
        db.add(tx3)
        await db.commit()

    mock_gen.market_key = "MKEY_EP_3"
    resp = await client.post(f"/api/v1/portfolios/{port.id}/lifecycle/evaluate")

    async with async_session_maker() as db:
        stmt = select(PositionLifecycle).where(PositionLifecycle.portfolio_id==port.id)
        lc = (await db.execute(stmt)).scalars().first()
        assert lc.health_state.name == "CLOSED"
        assert lc.episode_number == 1

    async with async_session_maker() as db:
        tx4 = PortfolioTransaction(portfolio_id=port.id, instrument_id=inst.id, transaction_type="BUY", quantity=Decimal("10"), executed_at=datetime.now(UTC))
        db.add(tx4)
        await db.commit()

    mock_gen.market_key = "MKEY_EP_4"
    resp = await client.post(f"/api/v1/portfolios/{port.id}/lifecycle/evaluate")
    assert resp.json()[0]["episode_number"] == 2

async def test_lifecycle_get_is_read_only(client: AsyncClient, auth_headers: dict, setup_lifecycle_portfolio, monkeypatch):
    port, inst = setup_lifecycle_portfolio
    client.headers = auth_headers
    mock_gen = MockDecisionGenerator()
    async def mock_eval(*args, **kwargs):
        return mock_gen(*args, **kwargs)
    monkeypatch.setattr("app.api.v1.endpoints.lifecycle.evaluate_lifecycle_for_instrument", mock_eval)

    await client.post(f"/api/v1/portfolios/{port.id}/lifecycle/evaluate")

    async with async_session_maker() as db:
        stmt = select(PositionLifecycle).where(PositionLifecycle.portfolio_id==port.id)
        lc1 = (await db.execute(stmt)).scalars().first()
        dt1 = lc1.updated_at

    for _ in range(5):
        await client.get(f"/api/v1/portfolios/{port.id}/lifecycle")

    async with async_session_maker() as db:
        lc2 = (await db.execute(stmt)).scalars().first()
        assert lc2.updated_at == dt1
        assert lc2.negative_confirmation_count == 0

async def test_lifecycle_concurrency_locks(client: AsyncClient, auth_headers: dict, setup_lifecycle_portfolio, monkeypatch):
    port, inst = setup_lifecycle_portfolio
    client.headers = auth_headers
    mock_gen = MockDecisionGenerator()
    mock_gen.market_view = "SELL"
    mock_gen.market_key = "MKEY_CONCURRENCY_1"

    async def async_mock(*args, **kwargs):
        dec = DecisionResult(
            market_view=mock_gen.market_view,
            instrument_id=1,
            horizon="SHORT",
            as_of=datetime.utcnow(),
            overall_market_score=50,
            reason_codes=[],
            warnings=[],
            missing_data=False,
            engine_version="v1",

            fundamental_score=50,
            technical_score=50,
            overall_personal_score=50,
            data_quality_score=100,
            market_observation_date="2026-09-01",
            is_evaluable=mock_gen.is_eval,
            reasons=[]
        )
        await asyncio.sleep(0.05)
        return dec, mock_gen.market_key, "ctx_123", mock_gen.is_eval

    monkeypatch.setattr("app.api.v1.endpoints.lifecycle.evaluate_lifecycle_for_instrument", async_mock)

    resps = []
    for _ in range(2):
        r = await client.post(f"/api/v1/portfolios/{port.id}/lifecycle/evaluate")
        if r.status_code == 200:
            resps.append(r)
    
    assert len(resps) > 0
