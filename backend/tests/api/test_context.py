import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.v1.endpoints.auth import get_current_user
from app.db.models import User

async def override_get_current_user():
    return User(id=1, email="test@example.com")

@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_context_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/instruments/THYAO/context")
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "THYAO"
        assert "news" in data["availability"]
        assert len(data["news"]) > 0
        assert data["news"][0]["is_synthetic"] == True
