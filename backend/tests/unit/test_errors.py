from fastapi.testclient import TestClient
from fastapi import APIRouter
from app.main import app
from app.core.errors import DomainException

router = APIRouter()

@router.get("/test-domain-error")
async def route_domain_error() -> dict[str, str]:
    raise DomainException(code="TEST_ERROR", message="Test message", status_code=400)

@router.get("/test-general-error")
async def route_general_error() -> dict[str, str]:
    raise ValueError("Test unexpected error")

app.include_router(router, prefix="/test-errors")
client = TestClient(app, raise_server_exceptions=False)

def test_domain_error_handler() -> None:
    response = client.get("/test-errors/test-domain-error")
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "TEST_ERROR"
    assert data["error"]["message"] == "Test message"
    assert "correlation_id" in data["error"]

def test_general_error_handler() -> None:
    response = client.get("/test-errors/test-general-error")
    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert "correlation_id" in data["error"]
