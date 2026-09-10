import random
import uuid
import pytest
from decimal import Decimal
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import Portfolio, PortfolioType, Instrument, User, ProviderMapping, InstrumentType
from app.db.session import async_session_maker
from app.main import app

user_mock_data = {"user_id": 1}

async def override_get_current_user():
    return User(id=user_mock_data["user_id"], email="test@example.com")

@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_paper_buy_authoritative_quote(monkeypatch):
    from app.market.dto import QuoteDTO
    from datetime import datetime, UTC
    async def mock_get_quotes(*args, **kwargs):
        return [QuoteDTO(
            symbol="AEFES.IS", price=15.50, data_state="LIVE",
            change_pct=0.0, high=15.5, low=15.5, open=15.5, previous_close=15.5,
            timestamp=datetime.now(UTC), source_name="yahoo", freshness_seconds=0
        )]
    monkeypatch.setattr("app.api.v1.endpoints.portfolios.registry.get_quotes", mock_get_quotes)

    async with async_session_maker() as db_session:
        user = User(email=f"test_{uuid.uuid4()}@test.com", password_hash="pw", is_active=True)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        user_mock_data["user_id"] = user.id

        portfolio = Portfolio(user_id=user.id, name="Test Paper", portfolio_type=PortfolioType.PAPER, currency="TRY")
        db_session.add(portfolio)
        
        inst = Instrument(symbol=f"TEST_{uuid.uuid4().hex[:4]}", name="Anadolu Efes", exchange="BIST", instrument_type=InstrumentType.STOCK)
        db_session.add(inst)
        await db_session.commit()
        await db_session.refresh(portfolio)
        await db_session.refresh(inst)

        mapping = ProviderMapping(instrument_id=inst.id, provider_name="yahoo", provider_symbol="AEFES.IS", is_primary=True)
        db_session.add(mapping)
        await db_session.commit()
        
        p_id = portfolio.id
        inst_id = inst.id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        dep_res = await client.post(
            f"/api/v1/portfolios/{p_id}/transactions",
            json={"transaction_type": "DEPOSIT", "quantity": 1000.0, "price": 1.0, "fee": 0.0}
        )
        assert dep_res.status_code == 200

        buy_res = await client.post(
            f"/api/v1/portfolios/{p_id}/trade",
            json={"side": "BUY", "instrument_id": inst_id, "quantity": 10.0}
        )
        assert buy_res.status_code == 200
        data = buy_res.json()
        assert float(data["quantity"]) == 10.0
        assert float(data["price"]) == 15.5

@pytest.mark.asyncio
async def test_paper_buy_budget_mode(monkeypatch):
    from app.market.dto import QuoteDTO
    from datetime import datetime, UTC
    async def mock_get_quotes(*args, **kwargs):
        return [QuoteDTO(
            symbol="AEFES.IS", price=20.00, data_state="LIVE",
            change_pct=0.0, high=20.0, low=20.0, open=20.0, previous_close=20.0,
            timestamp=datetime.now(UTC), source_name="yahoo", freshness_seconds=0
        )]
    monkeypatch.setattr("app.api.v1.endpoints.portfolios.registry.get_quotes", mock_get_quotes)

    async with async_session_maker() as db_session:
        user = User(email=f"test_{uuid.uuid4()}@test.com", password_hash="pw", is_active=True)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        user_mock_data["user_id"] = user.id

        portfolio = Portfolio(user_id=user.id, name="Test Paper 2", portfolio_type=PortfolioType.PAPER, currency="TRY")
        db_session.add(portfolio)
        
        inst = Instrument(symbol=f"GARAN_{uuid.uuid4().hex[:4]}", name="Garanti", exchange="BIST", instrument_type=InstrumentType.STOCK)
        db_session.add(inst)
        await db_session.commit()
        await db_session.refresh(portfolio)
        await db_session.refresh(inst)

        mapping = ProviderMapping(instrument_id=inst.id, provider_name="yahoo", provider_symbol="AEFES.IS", is_primary=True)
        db_session.add(mapping)
        await db_session.commit()
        
        p_id = portfolio.id
        inst_id = inst.id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            f"/api/v1/portfolios/{p_id}/transactions",
            json={"transaction_type": "DEPOSIT", "quantity": 1000.0, "price": 1.0, "fee": 0.0}
        )

        buy_res = await client.post(
            f"/api/v1/portfolios/{p_id}/trade",
            json={"side": "BUY", "instrument_id": inst_id, "budget_amount": 150.0}
        )
        assert buy_res.status_code == 200
        data = buy_res.json()
        assert float(data["quantity"]) == 7.0
        assert float(data["price"]) == 20.0
