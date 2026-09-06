"""
Auth endpoints: register, login, logout, /me.

Session model (canonical, stateful):
  - login  → create Session row (token = SHA-256 digest), return raw token in cookie (T04)
  - verify → look up digest in sessions table
  - logout → revoke session row
  - cookie → set in T04 (HttpOnly / Secure / SameSite=Lax)

T02/T03 scope:
  - register endpoint (Argon2id password hashing)
  - login endpoint (opaque session token creation, Redis rate-limit)
  - logout endpoint (session revocation)
  - /me endpoint (session-based user lookup)
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_client
from app.core.security import (
    generate_session_token,
    get_password_hash,
    hash_session_token,
    verify_password,
)
from app.db.models import Session as SessionModel
from app.db.models import User
from app.db.session import get_db_session
from app.schemas.user import UserCreate, UserResponse
from app.schemas.user import UserResponse as UserResponseSchema

logger = logging.getLogger(__name__)

router = APIRouter()

# Session TTL: 7 days.  Can be moved to settings later.
_SESSION_TTL_DAYS = 7

# Rate-limit: 50 failed login attempts per IP within 5 minutes -> 429.
_RATE_LIMIT_MAX_ATTEMPTS = 50
_RATE_LIMIT_WINDOW_SECONDS = 300


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _check_rate_limit(ip: str) -> None:
    """Raise 429 if the IP has exceeded failed-login threshold."""
    key = f"rate_limit:login:{ip}"
    try:
        attempts = await redis_client.get(key)
        if attempts and int(attempts) >= _RATE_LIMIT_MAX_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later.",
            )
    except HTTPException:
        raise
    except Exception:
        # Redis unavailable → fail-open (don't block legitimate users)
        logger.warning("Redis unavailable during rate-limit check; proceeding fail-open.")


async def _increment_rate_limit(ip: str) -> None:
    """Record a failed login attempt; best-effort."""
    key = f"rate_limit:login:{ip}"
    try:
        await redis_client.incr(key)
        await redis_client.expire(key, _RATE_LIMIT_WINDOW_SECONDS)
    except Exception:
        logger.warning("Redis unavailable; failed-login counter not incremented.")


async def _reset_rate_limit(ip: str) -> None:
    """Clear the rate-limit counter after a successful login; best-effort."""
    key = f"rate_limit:login:{ip}"
    try:
        await redis_client.delete(key)
    except Exception:
        logger.warning("Redis unavailable; failed-login counter not cleared.")


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


# ---------------------------------------------------------------------------
# Dependency: resolve current user from session cookie / Authorization header
# Used by T05+ endpoints.
# ---------------------------------------------------------------------------


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> User:
    """
    Resolve the authenticated user from the opaque session token.
    Looks for the token in the ``session_token`` cookie (set in T04).
    Raises 401 if missing, expired, or revoked.
    """
    raw_token = request.cookies.get("session_token")
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token_digest = hash_session_token(raw_token)
    result = await db.execute(
        select(SessionModel).where(
            SessionModel.token == token_digest,
            SessionModel.is_revoked.is_(False),
            SessionModel.expires_at > datetime.now(UTC),
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session invalid or expired",
        )

    user_result = await db.execute(
        select(User).where(User.id == session.user_id, User.is_active.is_(True))
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Kullanıcı kaydı oluştur",
)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> Any:
    """Register a new user account."""
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    db_user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        is_active=True,
        is_verified=False,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.post("/login", response_model=UserResponse)
async def login(
    user_in: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> Any:
    """
    Authenticate user and create a session.

    Sets an opaque session token in a Secure / HttpOnly / SameSite=Lax cookie.
    The same token is also echoed in ``X-Session-Token`` header for test readability
    (tests inject it as a cookie; real browsers receive the Set-Cookie header).
    """
    ip = _client_ip(request)
    await _check_rate_limit(ip)

    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_in.password, user.password_hash):  # type: ignore[arg-type]
        await _increment_rate_limit(ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account inactive",
        )

    await _reset_rate_limit(ip)

    # Create opaque session — store digest in DB, send raw token to browser
    raw_token = generate_session_token()
    token_digest = hash_session_token(raw_token)
    expires_at = datetime.now(UTC) + timedelta(days=_SESSION_TTL_DAYS)

    session = SessionModel(
        user_id=user.id,
        token=token_digest,
        expires_at=expires_at,
        is_revoked=False,
    )
    db.add(session)
    await db.commit()
    await db.refresh(user)

    content = UserResponseSchema.model_validate(user).model_dump(mode="json")
    response = JSONResponse(content=content, status_code=status.HTTP_200_OK)

    # T04: HttpOnly Secure SameSite=Lax cookie
    # secure=True requires HTTPS; in local dev (HTTP) the cookie still works because
    # browsers allow it on localhost. In production the HTTPS terminator ensures it.
    response.set_cookie(
        key="session_token",
        value=raw_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=_SESSION_TTL_DAYS * 86400,
        path="/",
    )
    # Also expose via header so tests can read it without parsing Set-Cookie
    response.headers["X-Session-Token"] = raw_token
    return response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> None:
    """Revoke the current session and expire the session cookie."""
    raw_token = request.cookies.get("session_token")
    if raw_token:
        token_digest = hash_session_token(raw_token)
        result = await db.execute(
            select(SessionModel).where(SessionModel.token == token_digest)
        )
        session = result.scalar_one_or_none()
        if session:
            session.is_revoked = True  # type: ignore[assignment]
            await db.commit()

    # Expire the cookie on the client — max_age=0 / expires=0 immediately
    response.delete_cookie(
        key="session_token", path="/", httponly=True, secure=True, samesite="lax"
    )


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)) -> Any:  # noqa: B008
    """Return the authenticated user's profile."""
    return current_user

