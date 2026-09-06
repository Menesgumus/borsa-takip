"""phase01_user_models

Revision ID: ce250a5f1627
Revises: e62787ff07e6
Create Date: 2026-09-05 23:26:52.554372

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ce250a5f1627'
down_revision: Union[str, Sequence[str], None] = 'e62787ff07e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# The risktolerance enum is created explicitly in upgrade() via DO block.
# create_type=False prevents SQLAlchemy from auto-emitting another CREATE TYPE.
risktolerance_enum = postgresql.ENUM('LOW', 'MEDIUM', 'HIGH', name='risktolerance', create_type=False)


def upgrade() -> None:
    """Upgrade schema."""
    # Create the risktolerance enum type explicitly and idempotently
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE risktolerance AS ENUM ('LOW', 'MEDIUM', 'HIGH');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('audit_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('action', sa.String(), nullable=False),
    sa.Column('ip_address', sa.String(), nullable=True),
    sa.Column('user_agent', sa.String(), nullable=True),
    sa.Column('details', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_table('sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_revoked', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sessions_id'), 'sessions', ['id'], unique=False)
    op.create_index(op.f('ix_sessions_token'), 'sessions', ['token'], unique=True)
    op.create_table('user_profiles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('timezone', sa.String(), nullable=False),
    sa.Column('risk_tolerance', risktolerance_enum, nullable=True),
    sa.Column('onboarding_completed', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_profiles_id'), 'user_profiles', ['id'], unique=False)
    op.drop_index(op.f('ix_trades_id'), table_name='trades')
    op.drop_index(op.f('ix_trades_symbol'), table_name='trades')
    op.drop_table('trades')
    op.drop_index(op.f('ix_positions_id'), table_name='positions')
    op.drop_index(op.f('ix_positions_symbol'), table_name='positions')
    op.drop_table('positions')
    op.drop_index(op.f('ix_portfolios_id'), table_name='portfolios')
    op.drop_table('portfolios')
    op.drop_index(op.f('ix_quotes_id'), table_name='quotes')
    op.drop_index(op.f('ix_quotes_symbol'), table_name='quotes')
    op.drop_index(op.f('ix_quotes_timestamp'), table_name='quotes')
    op.drop_table('quotes')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('quotes',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('symbol', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('price', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('quotes_pkey'))
    )
    op.create_index(op.f('ix_quotes_timestamp'), 'quotes', ['timestamp'], unique=False)
    op.create_index(op.f('ix_quotes_symbol'), 'quotes', ['symbol'], unique=False)
    op.create_index(op.f('ix_quotes_id'), 'quotes', ['id'], unique=False)
    op.create_table('portfolios',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('portfolios_pkey'))
    )
    op.create_index(op.f('ix_portfolios_id'), 'portfolios', ['id'], unique=False)
    op.create_table('positions',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('portfolio_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('symbol', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('quantity', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.Column('average_cost', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], name=op.f('positions_portfolio_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('positions_pkey'))
    )
    op.create_index(op.f('ix_positions_symbol'), 'positions', ['symbol'], unique=False)
    op.create_index(op.f('ix_positions_id'), 'positions', ['id'], unique=False)
    op.create_table('trades',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('portfolio_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('symbol', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('trade_type', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('quantity', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.Column('price', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.Column('executed_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], name=op.f('trades_portfolio_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('trades_pkey'))
    )
    op.create_index(op.f('ix_trades_symbol'), 'trades', ['symbol'], unique=False)
    op.create_index(op.f('ix_trades_id'), 'trades', ['id'], unique=False)
    op.drop_index(op.f('ix_user_profiles_id'), table_name='user_profiles')
    op.drop_table('user_profiles')
    op.drop_index(op.f('ix_sessions_token'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_id'), table_name='sessions')
    op.drop_table('sessions')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # Drop risktolerance enum type on downgrade
    op.execute("DROP TYPE IF EXISTS risktolerance")
    # ### end Alembic commands ###
