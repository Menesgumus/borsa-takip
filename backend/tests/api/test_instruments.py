import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import Instrument, InstrumentType, ProviderMapping, User
from app.db.session import async_session_maker
from app.main import app


async def override_get_current_user():
    return User(id=1, email="test@example.com")


@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()


from app.market.registry import registry
from app.market.mock_provider import MockMarketDataProvider

@pytest.fixture
async def setup_instruments():
    registry.register(MockMarketDataProvider(), is_primary=True)
    async with async_session_maker() as db_session:
        # cleanup first
        await db_session.execute(text("TRUNCATE TABLE instruments CASCADE"))
        await db_session.commit()

        inst1 = Instrument(
            symbol="BIST:GARAN",
            name="Garanti Bankasi",
            exchange="BIST",
            instrument_type=InstrumentType.STOCK,
        )
        inst2 = Instrument(
            symbol="BIST:THYAO",
            name="Turk Hava Yollari",
            exchange="BIST",
            instrument_type=InstrumentType.STOCK,
        )
        db_session.add_all([inst1, inst2])
        await db_session.commit()

        mapping1 = ProviderMapping(
            instrument_id=inst1.id,
            provider_name="mock",
            provider_symbol="GARAN.IS",
            is_primary=True,
        )
        db_session.add(mapping1)
        await db_session.commit()

    yield

    async with async_session_maker() as db_session:
        await db_session.execute(text("TRUNCATE TABLE instruments CASCADE"))
        await db_session.commit()


@pytest.mark.asyncio
async def test_list_instruments(setup_instruments):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/instruments")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        assert len(data["items"]) >= 2
        symbols = [item["symbol"] for item in data["items"]]
        assert "BIST:GARAN" in symbols
        assert "BIST:THYAO" in symbols


@pytest.mark.asyncio
async def test_list_instruments_search(setup_instruments):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/instruments?search=Hava")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["symbol"] == "BIST:THYAO"


@pytest.mark.asyncio
async def test_get_instrument(setup_instruments):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/instruments/BIST:GARAN")
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "BIST:GARAN"
        assert data["name"] == "Garanti Bankasi"


@pytest.mark.asyncio
async def test_get_instrument_quote(setup_instruments):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/instruments/BIST:GARAN/quote")
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "GARAN.IS"
        assert data["source_name"] == "mock"
        assert "price" in data


@pytest.mark.asyncio
async def test_get_instrument_history_not_found(setup_instruments):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/instruments/INVALID/history")
        assert response.status_code == 404
