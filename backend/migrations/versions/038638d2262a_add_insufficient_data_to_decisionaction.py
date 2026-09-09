"""Add INSUFFICIENT_DATA to DecisionAction

Revision ID: 038638d2262a
Revises: b26a56478fb3
Create Date: 2026-09-08 13:56:05.910086

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '038638d2262a'
down_revision: str | Sequence[str] | None = 'b26a56478fb3'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE decisionaction ADD VALUE IF NOT EXISTS 'INSUFFICIENT_DATA'")

def downgrade() -> None:
    """Downgrade schema."""
    pass
