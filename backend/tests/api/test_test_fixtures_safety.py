import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_test_fixtures_forbidden_in_production(async_client: AsyncClient, monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    
    response = await async_client.post("/api/v1/test-fixtures/lifecycle-override", json={
        "portfolio_id": 1,
        "instrument_id": 1,
        "health_state": "STABLE",
        "recommended_action": "HOLD"
    })
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Only available in test environment"
