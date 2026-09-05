import pytest
from alembic.config import Config
from alembic import command
import os

def test_migrations() -> None:
    # Get alembic configuration
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "../../alembic.ini"))
    alembic_cfg.set_main_option("script_location", os.path.join(os.path.dirname(__file__), "../../migrations"))
    
    # Test downgrade to base
    command.downgrade(alembic_cfg, "base")
    
    # Test upgrade to head
    command.upgrade(alembic_cfg, "head")
    
    # Test it's idempotent
    command.upgrade(alembic_cfg, "head")
