import os

os.environ["ENVIRONMENT"] = "test"
os.environ["POSTGRES_DB"] = "borsa_takip_test"
os.environ.setdefault("POSTGRES_HOST", "127.0.0.1")
os.environ["POSTGRES_PORT"] = "5432"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_PASSWORD"] = "postgres"
os.environ["REDIS_URL"] = "redis://127.0.0.1:6379/1"
os.environ["USE_MOCK_REDIS"] = "true"
os.environ["ENABLE_MOCK_MARKET_DATA"] = "true"

import pytest

from app.main import app


@pytest.fixture(autouse=True, scope="function")
async def clear_dependency_overrides():
    yield
    app.dependency_overrides.clear()
@pytest.fixture(autouse=True, scope="session")
def setup_test_database():
    # Run alembic upgrade head to ensure the test database has tables
    import os

    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "../alembic.ini"))
    alembic_cfg.set_main_option(
        "script_location", os.path.join(os.path.dirname(__file__), "../migrations")
    )
    command.upgrade(alembic_cfg, "head")
