"""Add editable site contacts."""
from alembic import op
import sqlalchemy as sa

revision = "d2e3f4a5b6c7"
down_revision = "c1d2e3f4a5b6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "site_contacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("hours", sa.String(300), nullable=True),
        sa.Column("email", sa.String(254), nullable=True),
        sa.CheckConstraint("id = 1", name="single_site_contacts"),
    )


def downgrade():
    op.drop_table("site_contacts")
