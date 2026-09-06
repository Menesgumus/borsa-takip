from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings

# Argon2id Hasher
# Using default parameters which are generally safe and fast enough.
# We can tune time_cost, memory_cost, and parallelism if needed.
pwd_hasher = PasswordHasher(
    time_cost=2, # Number of iterations
    memory_cost=65536, # 64MB memory cost
    parallelism=2 # 2 threads
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False

def get_password_hash(password: str) -> str:
    return pwd_hasher.hash(password)

def create_access_token(
    subject: str | int, expires_delta: timedelta | None = None
) -> str:
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        # Default to 30 minutes if not provided (should be configured in settings)
        expire = datetime.now(UTC) + timedelta(minutes=30)

    to_encode = {"exp": expire, "sub": str(subject)}

    # Use settings.SECRET_KEY, fallback to a dummy key if not set (for tests/dev)
    secret = getattr(settings, "SECRET_KEY", "fallback-secret-for-dev-only")

    encoded_jwt = jwt.encode(to_encode, secret, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> dict[str, Any] | None:
    secret = getattr(settings, "SECRET_KEY", "fallback-secret-for-dev-only")
    try:
        decoded_token = jwt.decode(token, secret, algorithms=["HS256"])
        return decoded_token
    except jwt.PyJWTError:
        return None
