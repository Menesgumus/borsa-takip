"""Add provenance fields to DecisionOutcome

Revision ID: e9644fc68961
Revises: 5a09821a85e9
Create Date: 2026-09-22 18:21:36.252163

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9644fc68961'
down_revision: Union[str, Sequence[str], None] = '5a09821a85e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('decision_outcomes', sa.Column('status', sa.String(length=50), server_default='UNTRUSTED_LEGACY_OUTCOME', nullable=False))
    op.add_column('decision_outcomes', sa.Column('provenance_metadata', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('decision_outcomes', 'provenance_metadata')
    op.drop_column('decision_outcomes', 'status')
