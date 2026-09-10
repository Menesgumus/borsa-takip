import os

os.environ["ENVIRONMENT"] = "test"
os.environ["POSTGRES_DB"] = "borsa_takip_test"

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
