"""Add editable about page."""
from alembic import op
import sqlalchemy as sa

revision = "e3f4a5b6c7d8"
down_revision = "d2e3f4a5b6c7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "site_about",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("blocks", sa.JSON(), nullable=False),
        sa.CheckConstraint("id = 1", name="single_site_about"),
    )


def downgrade():
    op.drop_table("site_about")
