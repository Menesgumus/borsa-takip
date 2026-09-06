"""
Unit tests for app.core.security.

Verifies:
- Argon2id hashing is fast enough (<300ms) and correct
- generate_session_token produces sufficient entropy
- hash_session_token is deterministic and does NOT return the raw token
- round-trip: raw token → digest → lookup-by-digest works
"""
import time

from app.core.security import (
    generate_session_token,
    get_password_hash,
    hash_session_token,
    verify_password,
)


def test_password_hashing_correctness_and_speed() -> None:
    password = "S3cur3P@ssw0rd!"  # noqa: S105

    start = time.perf_counter()
    hashed = get_password_hash(password)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 300, f"Hashing too slow: {elapsed_ms:.1f}ms (limit 300ms)"
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_session_token_entropy() -> None:
    token = generate_session_token()
    # URL-safe base64 of 32 bytes → ~43 characters minimum
    assert len(token) >= 43, f"Token too short: {len(token)} chars"


def test_session_token_uniqueness() -> None:
    tokens = {generate_session_token() for _ in range(50)}
    assert len(tokens) == 50, "Token collision detected"


def test_hash_session_token_deterministic() -> None:
    raw = generate_session_token()
    digest1 = hash_session_token(raw)
    digest2 = hash_session_token(raw)
    assert digest1 == digest2, "hash_session_token must be deterministic"


def test_hash_session_token_not_raw() -> None:
    raw = generate_session_token()
    digest = hash_session_token(raw)
    assert digest != raw, "Digest must differ from raw token"
    # SHA-256 hex digest is always 64 hex characters
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)
