"""Add durable per-user AI usage accounting."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260717_0002"
down_revision: Union[str, None] = "20260717_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_usage_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("feature", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_usage_events_created_at", "ai_usage_events", ["created_at"], unique=False)
    op.create_index("ix_ai_usage_events_feature", "ai_usage_events", ["feature"], unique=False)
    op.create_index("ix_ai_usage_events_id", "ai_usage_events", ["id"], unique=False)
    op.create_index("ix_ai_usage_events_user_id", "ai_usage_events", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("ai_usage_events")
