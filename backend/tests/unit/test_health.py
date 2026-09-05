from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_live() -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "X-Correlation-ID" in response.headers


def test_health_ready() -> None:
    # Assuming the DB and Redis are up in tests, or we mock them.
    # We will test the actual endpoint which uses the integration services.
    response = client.get("/health/ready")
    assert response.status_code in (200, 503)
    data = response.json()
    assert data["status"] in ("ok", "error")
