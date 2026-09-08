from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    ENVIRONMENT: Literal["development", "production", "test"] = "development"

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "fake_password"  # noqa: S105
    POSTGRES_DB: str = "borsa_takip_dev"
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
