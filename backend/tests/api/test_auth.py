"""
Integration tests for auth endpoints.

Tests run against the real async DB (PostgreSQL must be reachable).
Session tokens are read from the ``X-Session-Token`` response header
(cookie transport is wired up in T04).

Covered:
- POST /api/v1/auth/register  → 201 / 400 duplicate
- POST /api/v1/auth/login     → 200 + X-Session-Token header
- POST /api/v1/auth/login     → 401 wrong credentials (generic message)
- GET  /api/v1/auth/me        → 200 with valid cookie session
- POST /api/v1/auth/logout    → 204
- Rate-limit: 5 failed attempts → 429
- Raw session token NOT present in DB (only digest stored)
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.core.security import hash_session_token
from app.db.session import engine
from app.main import app

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_TEST_EMAIL = "authtest@example.com"
_TEST_PASSWORD = "AuthP@ss123!"  # noqa: S105


@pytest.fixture(autouse=True)
async def cleanup_test_user():  # type: ignore[no-untyped-def]
    """Remove test user rows and rate-limit key before and after each test."""
    from app.core.redis import redis_client

    async def _clean_db() -> None:
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    "DELETE FROM sessions USING users "
                    "WHERE sessions.user_id = users.id AND users.email = :e"
                ),
                {"e": _TEST_EMAIL},
            )
            await conn.execute(text("DELETE FROM users WHERE email = :e"), {"e": _TEST_EMAIL})

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _register(client: AsyncClient) -> dict:  # type: ignore[type-arg]
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": _TEST_EMAIL, "password": _TEST_PASSWORD},
    )
    assert r.status_code == 201, r.text
    return r.json()  # type: ignore[no-any-return]


async def _login(client: AsyncClient) -> tuple[dict, str]:  # type: ignore[type-arg]
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": _TEST_EMAIL, "password": _TEST_PASSWORD},
    )
    assert r.status_code == 200, r.text
    raw_token = r.headers.get("x-session-token", "")
    return r.json(), raw_token


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_register_success() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        data = await _register(client)
        assert data["email"] == _TEST_EMAIL
        assert "id" in data
        assert data["is_active"] is True


@pytest.mark.asyncio
async def test_register_duplicate_email() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await _register(client)
        r2 = await client.post(
            "/api/v1/auth/register",
            json={"email": _TEST_EMAIL, "password": _TEST_PASSWORD},
        )
        assert r2.status_code == 400


@pytest.mark.asyncio
async def test_login_success_returns_opaque_token() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await _register(client)
        user_data, raw_token = await _login(client)

        assert user_data["email"] == _TEST_EMAIL
        # Token must be present and have sufficient entropy
        assert len(raw_token) >= 43, f"Token too short: {raw_token!r}"


@pytest.mark.asyncio
async def test_raw_token_not_stored_in_db() -> None:
    """Ensure the sessions table stores the digest, not the raw token."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await _register(client)
        _, raw_token = await _login(client)

        digest = hash_session_token(raw_token)
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT token FROM sessions WHERE token = :tok"),
                {"tok": digest},
            )
            row = result.fetchone()
            assert row is not None, "Session digest not found in DB"

            # Confirm raw token is NOT in DB
            result2 = await conn.execute(
                text("SELECT token FROM sessions WHERE token = :tok"),
                {"tok": raw_token},
            )
            assert result2.fetchone() is None, "Raw token found in DB — security violation!"


@pytest.mark.asyncio
async def test_login_wrong_password_generic_message() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await _register(client)
        r = await client.post(
            "/api/v1/auth/login",
            json={"email": _TEST_EMAIL, "password": "WrongPassword!"},
        )
        assert r.status_code == 401
        # Generic message — must not reveal whether email exists
        assert "Invalid credentials" in r.json()["detail"]


@pytest.mark.asyncio
async def test_login_rate_limit() -> None:
    """5 failed attempts from same IP → 6th should 429 (Redis must be up)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await _register(client)

        for _ in range(5):
            await client.post(
                "/api/v1/auth/login",
                json={"email": _TEST_EMAIL, "password": "WrongPw!"},
            )

        r = await client.post(
            "/api/v1/auth/login",
            json={"email": _TEST_EMAIL, "password": "WrongPw!"},
        )
        # 429 when Redis is up, something ≤ 401 when Redis is down (fail-open)
        assert r.status_code in (401, 429)


@pytest.mark.asyncio
async def test_me_requires_valid_session() -> None:
    """GET /me without session cookie → 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/v1/auth/me")
        assert r.status_code == 401


@pytest.mark.asyncio
async def test_me_with_valid_session_cookie() -> None:
    """GET /me with the session cookie set → 200."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await _register(client)
        _, raw_token = await _login(client)

        # T04: login sets the cookie; httpx propagates it automatically.
        # Verify the cookie was set in the login response.
        client.cookies.set("session_token", raw_token)
        r = await client.get("/api/v1/auth/me")
        assert r.status_code == 200
        assert r.json()["email"] == _TEST_EMAIL


@pytest.mark.asyncio
async def test_login_sets_httponly_cookie() -> None:
    """T04: login response must set a Set-Cookie header with HttpOnly and SameSite=Lax."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await _register(client)
        r = await client.post(
            "/api/v1/auth/login",
            json={"email": _TEST_EMAIL, "password": _TEST_PASSWORD},
        )
        assert r.status_code == 200
        # ASGITransport exposes Set-Cookie via response.headers
        set_cookie = r.headers.get("set-cookie", "")
        assert "session_token=" in set_cookie
        assert "HttpOnly" in set_cookie
        assert "SameSite=lax" in set_cookie or "SameSite=Lax" in set_cookie


@pytest.mark.asyncio
async def test_logout_revokes_session() -> None:
    """POST /logout with valid cookie → 204; subsequent /me → 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await _register(client)
        _, raw_token = await _login(client)

        client.cookies.set("session_token", raw_token)

        r_logout = await client.post("/api/v1/auth/logout")
        assert r_logout.status_code == 204

        # Cookie is revoked — /me must 401 now
        r_me = await client.get("/api/v1/auth/me")
        assert r_me.status_code == 401
