"""add materials

Revision ID: 8f5a2c1d9b34
Revises: 2c328f7462b9
Create Date: 2026-09-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f5a2c1d9b34"
down_revision: Union[str, Sequence[str], None] = "2c328f7462b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "materials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name")
    )

    op.add_column(
        "products",
        sa.Column("material_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "fk_products_material_id_materials",
        "products",
        "materials",
        ["material_id"],
        ["id"],
        ondelete="SET NULL"
    )

    op.add_column(
        "furniture_requests",
        sa.Column("material_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "fk_furniture_requests_material_id_materials",
        "furniture_requests",
        "materials",
        ["material_id"],
        ["id"],
        ondelete="SET NULL"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_furniture_requests_material_id_materials",
        "furniture_requests",
        type_="foreignkey"
    )
    op.drop_column("furniture_requests", "material_id")

    op.drop_constraint(
        "fk_products_material_id_materials",
        "products",
        type_="foreignkey"
    )
    op.drop_column("products", "material_id")

    op.drop_table("materials")
