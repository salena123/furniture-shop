"""remove request source

Revision ID: c1d2e3f4a5b6
Revises: b8c7d6e5f4a3
Create Date: 2026-09-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, Sequence[str], None] = "b8c7d6e5f4a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(op.f("ix_furniture_requests_source"), table_name="furniture_requests")

    with op.batch_alter_table("furniture_requests") as batch_op:
        batch_op.drop_column("source")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("furniture_requests") as batch_op:
        batch_op.add_column(
            sa.Column(
                "source",
                sa.String(length=50),
                server_default="catalog",
                nullable=False,
            )
        )

    op.create_index(
        op.f("ix_furniture_requests_source"),
        "furniture_requests",
        ["source"],
        unique=False,
    )
