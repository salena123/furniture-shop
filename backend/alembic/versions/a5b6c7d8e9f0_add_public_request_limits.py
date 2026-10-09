"""Add rate limits for public enquiries."""
from alembic import op
import sqlalchemy as sa

revision = 'a5b6c7d8e9f0'
down_revision = 'f4a5b6c7d8e9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'public_request_rate_limits',
        sa.Column('key', sa.String(80), primary_key=True),
        sa.Column('attempts', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.Integer(), nullable=False),
    )
    op.create_index(
        'ix_public_request_rate_limits_expires_at',
        'public_request_rate_limits',
        ['expires_at'],
    )


def downgrade():
    op.drop_table('public_request_rate_limits')
