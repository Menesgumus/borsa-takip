import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.db.session import engine
from app.main import app

_TEST_EMAIL = "profile_test@example.com"
_TEST_PASSWORD = "ProfileP@ss123!"  # noqa: S105
_TEST_EMAIL2 = "hacker@example.com"
_TEST_PASSWORD2 = "HackerP@ss123!"  # noqa: S105


@pytest.fixture(autouse=True)
async def cleanup_test_data():  # type: ignore[no-untyped-def]
    """Remove test users and their profiles."""
    from app.core.redis import redis_client

    async def _clean_db() -> None:
        async with engine.begin() as conn:
            # Cascading deletes will handle profiles and sessions
            await conn.execute(
                text("DELETE FROM users WHERE email IN (:e1, :e2)"),
                {"e1": _TEST_EMAIL, "e2": _TEST_EMAIL2},
            )

    async def _clean_redis() -> None:
        try:
            keys = await redis_client.keys("rate_limit:login:*")
            if keys:
                await redis_client.delete(*keys)
        except Exception:  # noqa: S110
            pass

    await _clean_db()
    await _clean_redis()
    yield
    await _clean_db()
    await _clean_redis()


async def _register(client: AsyncClient, email: str, password: str) -> None:
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert r.status_code == 201


async def _login(client: AsyncClient, email: str, password: str) -> str:
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert r.status_code == 200
    return str(r.headers.get("x-session-token", ""))


@pytest.mark.asyncio
async def test_get_profile_auto_creates() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await _register(client, _TEST_EMAIL, _TEST_PASSWORD)
        token = await _login(client, _TEST_EMAIL, _TEST_PASSWORD)
        client.cookies.set("session_token", token)

        # First request should auto-create
        r = await client.get("/api/v1/users/profile")
        assert r.status_code == 200
        data = r.json()
        assert data["timezone"] == "Europe/Istanbul"
        assert data["onboarding_completed"] is False
        assert data["first_name"] is None


@pytest.mark.asyncio
async def test_update_profile() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await _register(client, _TEST_EMAIL, _TEST_PASSWORD)
        token = await _login(client, _TEST_EMAIL, _TEST_PASSWORD)
        client.cookies.set("session_token", token)

        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "risk_tolerance": "HIGH",
            "onboarding_completed": True,
        }

        r = await client.put("/api/v1/users/profile", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["risk_tolerance"] == "HIGH"
        assert data["onboarding_completed"] is True


@pytest.mark.asyncio
async def test_profile_idor_protection() -> None:
    """
    Ensure users can only access their own profile.
    Because the API doesn't accept a user_id parameter and strictly relies
    on the current session, it's structurally immune to IDOR, but we verify
    isolation explicitly.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create victim
        await _register(client, _TEST_EMAIL, _TEST_PASSWORD)
        token1 = await _login(client, _TEST_EMAIL, _TEST_PASSWORD)
        client.cookies.set("session_token", token1)

        # Victim sets profile
        r1 = await client.put(
            "/api/v1/users/profile", json={"first_name": "Victim", "risk_tolerance": "LOW"}
        )
        assert r1.status_code == 200

        # Create attacker
        await _register(client, _TEST_EMAIL2, _TEST_PASSWORD2)
        token2 = await _login(client, _TEST_EMAIL2, _TEST_PASSWORD2)
        client.cookies.set("session_token", token2)

        # Attacker tries to read profile (can only read theirs)
        r2 = await client.get("/api/v1/users/profile")
        assert r2.status_code == 200
        assert r2.json()["first_name"] is None  # Getting attacker's own blank profile

        # Attacker tries to put
        r3 = await client.put("/api/v1/users/profile", json={"first_name": "Attacker"})
        assert r3.status_code == 200
        assert r3.json()["first_name"] == "Attacker"

        # Verify victim's profile was not changed
        client.cookies.set("session_token", token1)
        r4 = await client.get("/api/v1/users/profile")
        assert r4.json()["first_name"] == "Victim"
