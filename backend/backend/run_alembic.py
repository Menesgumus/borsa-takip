import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

if __name__ == '__main__':
    os.environ["ENVIRONMENT"] = "test"
    os.environ["POSTGRES_DB"] = "borsa_takip_test"
    os.environ.setdefault("POSTGRES_HOST", "127.0.0.1")
    os.environ.setdefault("POSTGRES_PORT", "5434")
    os.environ.setdefault("POSTGRES_USER", "qa_user")
    os.environ.setdefault("POSTGRES_PASSWORD", "qa_password")
    os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:6381/0")
    os.environ.setdefault("ENABLE_MOCK_MARKET_DATA", "true")

    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config("alembic.ini")
    print("Running alembic current:")
    command.current(alembic_cfg)

    print("Running alembic upgrade head:")
    command.upgrade(alembic_cfg, "head")
