"""
Security utilities for password hashing (Argon2id) and opaque session token generation.

Opaque session token approach:
- Raw token: generated with `secrets.token_urlsafe(32)` (256-bit entropy)
- DB storage: SHA-256 digest of the raw token (not the raw token itself)
- Browser: raw token stored in HttpOnly Secure SameSite cookie (set in T04)

This prevents session fixation from DB leaks: an attacker with DB access
gets only token digests, not usable session values.
"""

import hashlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# ---------------------------------------------------------------------------
# Password hashing (Argon2id)
# ---------------------------------------------------------------------------

# time_cost=2, memory_cost=64MB, parallelism=2 → ~85ms on dev hardware.
# Well within the 300ms budget specified in Phase 01 plan.
_pwd_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=65536,  # 64 MiB
    parallelism=2,
)


def get_password_hash(password: str) -> str:
    """Return an Argon2id hash of *password*."""
    return _pwd_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify *plain_password* against the stored Argon2id hash."""
    try:
        return _pwd_hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False


# ---------------------------------------------------------------------------
# Opaque session token
# ---------------------------------------------------------------------------

_TOKEN_BYTES = 32  # 256 bits of entropy


def generate_session_token() -> str:
    """
    Generate a cryptographically secure opaque session token.

    Returns the *raw* token that should be placed in the user's cookie.
    Store only the *digest* in the database (see `hash_session_token`).
    """
    return secrets.token_urlsafe(_TOKEN_BYTES)


def hash_session_token(raw_token: str) -> str:
    """
    Return the SHA-256 hex-digest of *raw_token*.

    This digest is what gets stored in the ``sessions.token`` column.
    The raw token never touches the database.
    """
    return hashlib.sha256(raw_token.encode()).hexdigest()
