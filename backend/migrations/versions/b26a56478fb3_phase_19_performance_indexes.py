"""phase_19_performance_indexes

Revision ID: b26a56478fb3
Revises: 67c1201262e1
Create Date: 2026-09-08 02:38:23.632921

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b26a56478fb3'
down_revision: Union[str, Sequence[str], None] = '67c1201262e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index('idx_portfolio_tx_executed_at', 'portfolio_transactions', ['portfolio_id', 'executed_at'])
    op.create_index('idx_ohlcv_daily_time', 'ohlcv_daily', ['instrument_id', sa.text('timestamp DESC')])
    op.create_index('idx_decision_snapshots_instrument', 'decision_snapshots', ['instrument_id', sa.text('calculated_at DESC')])
    op.create_index('idx_trade_journals_portfolio_time', 'trade_journals', ['portfolio_id', sa.text('created_at DESC')])

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_trade_journals_portfolio_time', table_name='trade_journals')
    op.drop_index('idx_decision_snapshots_instrument', table_name='decision_snapshots')
    op.drop_index('idx_ohlcv_daily_time', table_name='ohlcv_daily')
    op.drop_index('idx_portfolio_tx_executed_at', table_name='portfolio_transactions')
