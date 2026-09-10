import os

from alembic import command
from alembic.config import Config


def test_migrations() -> None:
    # Get alembic configuration
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "../../alembic.ini"))
    alembic_cfg.set_main_option(
        "script_location", os.path.join(os.path.dirname(__file__), "../../migrations")
    )

    from app.core.config import settings
    assert settings.ENVIRONMENT == "test", "Migrations test must run in test environment"
    assert "test" in settings.POSTGRES_DB.lower(), f"Refusing to run downgrade on non-test DB: {settings.POSTGRES_DB}"

    # Test downgrade to base
    command.downgrade(alembic_cfg, "base")

    # Test upgrade to head
    command.upgrade(alembic_cfg, "head")

    # Test it's idempotent
    command.upgrade(alembic_cfg, "head")
