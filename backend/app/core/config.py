from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    ENVIRONMENT: Literal["development", "production", "test", "calibration"] = "development"

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "fake_password"  # noqa: S105
    POSTGRES_DB: str = "borsa_takip_dev"

    @model_validator(mode="after")
    def validate_database_guards(self) -> "Settings":
        if self.ENVIRONMENT == "test":
            if "test" not in self.POSTGRES_DB.lower():
                raise ValueError(
                    f"REFUSING TO RUN TESTS AGAINST NON-TEST DATABASE:\n"
                    f"{self.POSTGRES_DB}\n"
                    f"The test database must explicitly identify itself as disposable (e.g. borsa_takip_test)."
                )
        if self.ENVIRONMENT == "calibration":
            if "calibration" not in self.POSTGRES_DB.lower():
                raise ValueError(
                    f"REFUSING TO RUN CALIBRATION AGAINST NON-CALIBRATION DATABASE:\n"
                    f"{self.POSTGRES_DB}\n"
                    f"The calibration database must explicitly identify itself as calibration."
                )
        return self
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5433

    REDIS_URL: str = "redis://localhost:6379/0"

    EVDS_API_KEY: str | None = None

    # Mock Data
    ENABLE_MOCK_MARKET_DATA: bool = False

    # Session TTL (days) — used by auth endpoint; can be overridden in .env
    SESSION_TTL_DAYS: int = 7

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
