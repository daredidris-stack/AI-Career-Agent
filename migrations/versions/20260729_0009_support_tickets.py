"""Add support tickets."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260729_0009"
down_revision: Union[str, None] = "20260729_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "support_tickets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("subject", sa.String(length=200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=30),
            server_default="new",
            nullable=False,
        ),
        sa.Column("admin_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_support_tickets_id", "support_tickets", ["id"])
    op.create_index(
        "ix_support_tickets_user_id",
        "support_tickets",
        ["user_id"],
    )
    op.create_index(
        "ix_support_tickets_status",
        "support_tickets",
        ["status"],
    )


def downgrade() -> None:
    op.drop_table("support_tickets")
