import logging
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import User, UserProfile
from app.db.session import get_db_session
from app.schemas.profile import UserProfileResponse, UserProfileUpdate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> Any:
    """
    Get current user's profile.
    Uses the authenticated session to infer user context, inherently preventing IDOR.
    If the profile doesn't exist, it creates a default one.
    """
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()

    if not profile:
        profile = UserProfile(
            user_id=current_user.id,
            timezone="Europe/Istanbul",
            onboarding_completed=False,
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    return profile


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    profile_in: UserProfileUpdate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> Any:
    """
    Update current user's profile.
    Uses the authenticated session to infer user context.
    """
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()

    if not profile:
        profile = UserProfile(
            user_id=current_user.id,
            timezone="Europe/Istanbul",
            onboarding_completed=False,
        )
        db.add(profile)

    update_data = profile_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)

    return profile
