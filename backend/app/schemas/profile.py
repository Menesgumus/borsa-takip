from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import RiskTolerance


class UserProfileBase(BaseModel):
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    timezone: str = Field(default="Europe/Istanbul", max_length=50)
    risk_tolerance: RiskTolerance | None = None


class UserProfileUpdate(UserProfileBase):
    onboarding_completed: bool | None = None


class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    onboarding_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
