from app.core.config import Settings


def test_config_defaults() -> None:
    # Explicitly clear environment for this test to rely purely on defaults
    # Pydantic Settings reads from environment variables, so we mock an empty one.
    settings = Settings(ENVIRONMENT="development")
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
import os

import pytest


def test_settings_guard():
    # Prove that test + borsa_takip_test works
    os.environ["ENVIRONMENT"] = "test"
    os.environ["POSTGRES_DB"] = "borsa_takip_test"
    # We must reload/re-evaluate the Settings class
    # Since config.py is already loaded, we import the class
    from app.core.config import Settings
    s1 = Settings()
    assert s1.ENVIRONMENT == "test"
    assert s1.POSTGRES_DB == "borsa_takip_test"

    # Prove that test + borsa_takip_dev aborts
    os.environ["POSTGRES_DB"] = "borsa_takip_dev"
    with pytest.raises(ValueError) as excinfo:
        Settings()
    assert "REFUSING TO RUN TESTS AGAINST NON-TEST DATABASE" in str(excinfo.value)

    # Clean up environment to not break other tests if they reload
    os.environ["POSTGRES_DB"] = "borsa_takip_test"
