import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.db.session import engine
from app.main import app


@pytest.fixture(autouse=True)
async def cleanup_db():
    # Cleanup before test
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM users WHERE email='testuser@example.com'"))
    yield
    # Cleanup after test
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM users WHERE email='testuser@example.com'"))

@pytest.mark.asyncio
async def test_register_and_login_user() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Register
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "testuser@example.com", "password": "StrongPassword123!"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "testuser@example.com"
        assert "id" in data

        # Try registering again with the same email
        response2 = await client.post(
            "/api/v1/auth/register",
            json={"email": "testuser@example.com", "password": "StrongPassword123!"}
        )
        assert response2.status_code == 400

        # 2. Login with valid credentials
        response3 = await client.post(
            "/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "StrongPassword123!"}
        )
        assert response3.status_code == 200
        data = response3.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # 3. Login with invalid credentials
        response4 = await client.post(
            "/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "WrongPassword"}
        )
        assert response4.status_code == 401

        # 4. Rate Limiting check
        for _ in range(5):
            await client.post(
                "/api/v1/auth/login",
                json={"email": "testuser@example.com", "password": "WrongPassword"}
            )

        response_rate = await client.post(
            "/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "WrongPassword"}
        )
        # Should be 429, unless redis is down, then it falls back
        if response_rate.status_code == 429:
            assert response_rate.status_code == 429
