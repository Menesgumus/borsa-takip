import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_test_fixtures_forbidden_in_production(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    
    from app.main import app
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/test-fixtures/lifecycle-override", json={
            "portfolio_id": 1,
            "instrument_id": 1,
            "health_state": "STABLE",
            "recommended_action": "HOLD"
        })
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Only available in test environment"
