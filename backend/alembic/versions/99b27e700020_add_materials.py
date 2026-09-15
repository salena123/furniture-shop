"""remove old material extra fields

Revision ID: 99b27e700020
Revises: 8f5a2c1d9b34
Create Date: 2026-09-16 03:32:21.069253

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99b27e700020'
down_revision: Union[str, Sequence[str], None] = '8f5a2c1d9b34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {
        column["name"]
        for column in inspector.get_columns("materials")
    }

    if "is_active" in columns:
        op.drop_column("materials", "is_active")

    if "sort_order" in columns:
        op.drop_column("materials", "sort_order")


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {
        column["name"]
        for column in inspector.get_columns("materials")
    }

    if "sort_order" not in columns:
        op.add_column(
            "materials",
            sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False)
        )

    if "is_active" not in columns:
        op.add_column(
            "materials",
            sa.Column("is_active", sa.Boolean(), server_default="TRUE", nullable=False)
        )
