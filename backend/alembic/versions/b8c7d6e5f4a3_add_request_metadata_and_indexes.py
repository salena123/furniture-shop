"""add request metadata and indexes

Revision ID: b8c7d6e5f4a3
Revises: 99b27e700020
Create Date: 2026-09-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b8c7d6e5f4a3"
down_revision: Union[str, Sequence[str], None] = "99b27e700020"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("furniture_requests") as batch_op:
        batch_op.add_column(sa.Column("city", sa.String(length=100), nullable=True))
        batch_op.add_column(
            sa.Column(
                "source",
                sa.String(length=50),
                server_default="catalog",
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column("preferred_contact_time", sa.String(length=100), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "personal_data_consent",
                sa.Boolean(),
                server_default=sa.false(),
                nullable=False,
            )
        )

    op.create_index(
        op.f("ix_products_category_id"),
        "products",
        ["category_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_products_material_id"),
        "products",
        ["material_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_products_is_active"),
        "products",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        op.f("ix_furniture_requests_product_id"),
        "furniture_requests",
        ["product_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_furniture_requests_material_id"),
        "furniture_requests",
        ["material_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_furniture_requests_status"),
        "furniture_requests",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_furniture_requests_assigned_manager_id"),
        "furniture_requests",
        ["assigned_manager_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_furniture_requests_created_at"),
        "furniture_requests",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_furniture_requests_city"),
        "furniture_requests",
        ["city"],
        unique=False,
    )
    op.create_index(
        op.f("ix_furniture_requests_source"),
        "furniture_requests",
        ["source"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_furniture_requests_source"), table_name="furniture_requests")
    op.drop_index(op.f("ix_furniture_requests_city"), table_name="furniture_requests")
    op.drop_index(
        op.f("ix_furniture_requests_created_at"),
        table_name="furniture_requests",
    )
    op.drop_index(
        op.f("ix_furniture_requests_assigned_manager_id"),
        table_name="furniture_requests",
    )
    op.drop_index(op.f("ix_furniture_requests_status"), table_name="furniture_requests")
    op.drop_index(
        op.f("ix_furniture_requests_material_id"),
        table_name="furniture_requests",
    )
    op.drop_index(
        op.f("ix_furniture_requests_product_id"),
        table_name="furniture_requests",
    )
    op.drop_index(op.f("ix_products_is_active"), table_name="products")
    op.drop_index(op.f("ix_products_material_id"), table_name="products")
    op.drop_index(op.f("ix_products_category_id"), table_name="products")

    with op.batch_alter_table("furniture_requests") as batch_op:
        batch_op.drop_column("personal_data_consent")
        batch_op.drop_column("preferred_contact_time")
        batch_op.drop_column("source")
        batch_op.drop_column("city")
