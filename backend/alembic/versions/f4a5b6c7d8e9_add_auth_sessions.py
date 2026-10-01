"""Revocable sessions and shared login rate limits."""
from alembic import op
import sqlalchemy as sa

revision = 'f4a5b6c7d8e9'
down_revision = 'e3f4a5b6c7d8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('auth_version', sa.Integer(), nullable=False, server_default='0'))
    op.create_table('auth_sessions',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False))
    op.create_index('ix_auth_sessions_user_id', 'auth_sessions', ['user_id'])
    op.create_index('ix_auth_sessions_expires_at', 'auth_sessions', ['expires_at'])
    op.create_table('auth_rate_limits',
        sa.Column('key', sa.String(80), primary_key=True),
        sa.Column('attempts', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.Integer(), nullable=False))
    op.create_index('ix_auth_rate_limits_expires_at', 'auth_rate_limits', ['expires_at'])


def downgrade():
    op.drop_table('auth_rate_limits')
    op.drop_table('auth_sessions')
    op.drop_column('users', 'auth_version')
