"""Remove INSUFFICIENT_DATA from DecisionAction and add decision_state

Revision ID: ea09294646b8
Revises: 038638d2262a
Create Date: 2026-09-08 14:18:49.293593

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea09294646b8'
down_revision: Union[str, Sequence[str], None] = '038638d2262a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Migrate any rows that might have INSUFFICIENT_DATA back to HOLD
    op.execute("UPDATE decision_snapshots SET action = 'HOLD' WHERE action::text = 'INSUFFICIENT_DATA'")

    # Create decisionstate enum
    op.execute("CREATE TYPE decisionstate AS ENUM ('AVAILABLE', 'INSUFFICIENT_DATA', 'UNAVAILABLE')")

    # Add decision_state column
    op.execute("ALTER TABLE decision_snapshots ADD COLUMN decision_state decisionstate NOT NULL DEFAULT 'AVAILABLE'")

    # Safely recreate decisionaction enum without INSUFFICIENT_DATA
    op.execute("ALTER TYPE decisionaction RENAME TO decisionaction_old")
    op.execute("CREATE TYPE decisionaction AS ENUM ('STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL')")
    op.execute("ALTER TABLE decision_snapshots ALTER COLUMN action DROP DEFAULT")
    op.execute("ALTER TABLE decision_snapshots ALTER COLUMN action TYPE decisionaction USING action::text::decisionaction")
    op.execute("DROP TYPE decisionaction_old")

def downgrade() -> None:
    op.execute("ALTER TYPE decisionaction ADD VALUE IF NOT EXISTS 'INSUFFICIENT_DATA'")
    op.execute("ALTER TABLE decision_snapshots DROP COLUMN decision_state")
    op.execute("DROP TYPE decisionstate")
