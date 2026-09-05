from app.core.config import Settings


def test_config_defaults() -> None:
    # Explicitly clear environment for this test to rely purely on defaults
    # Pydantic Settings reads from environment variables, so we mock an empty one.
    settings = Settings(_env_file=None, ENVIRONMENT="development")
    assert settings.ENVIRONMENT == "development"
    assert settings.POSTGRES_USER == "postgres"


def test_database_url_property() -> None:
    settings = Settings(
        POSTGRES_USER="test_user",
        POSTGRES_PASSWORD="test_password",
        POSTGRES_HOST="test_host",
        POSTGRES_PORT=1234,
        POSTGRES_DB="test_db",
    )
    assert (
        settings.database_url
        == "postgresql+asyncpg://test_user:test_password@test_host:1234/test_db"
    )
