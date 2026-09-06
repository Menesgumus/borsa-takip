from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.models import User
from app.db.session import get_db_session
from app.schemas.user import Token, UserCreate, UserResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db_session)) -> Any:
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        password_hash=hashed_password,
        is_active=True,
        is_verified=False
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user

@router.post("/login", response_model=Token)
async def login(user_in: UserCreate, request: Request, db: AsyncSession = Depends(get_db_session)) -> Any:
    # Rate Limiting Logic (Redis)
    client_ip = request.client.host if request.client else "unknown"
    rate_limit_key = f"rate_limit:login:{client_ip}"

    from app.core.redis import redis_client

    try:
        attempts = await redis_client.get(rate_limit_key)
        if attempts and int(attempts) >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts, please try again later."
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        # If redis is down, we might want to bypass or log it
        pass

    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_in.password, user.password_hash):  # type: ignore[arg-type]
        # Increment failed attempt
        try:
            await redis_client.incr(rate_limit_key)
            await redis_client.expire(rate_limit_key, 300) # 5 minutes lockout
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Reset limit on success
    try:
        await redis_client.delete(rate_limit_key)
    except Exception:
        pass

    access_token = create_access_token(subject=user.id)  # type: ignore[arg-type]
    return {"access_token": access_token, "token_type": "bearer"}
