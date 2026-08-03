"""Add interview practice attempts."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260729_0010"
down_revision: Union[str, None] = "20260729_0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "interview_practice_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=200), nullable=False),
        sa.Column(
            "interview_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column(
            "rubric_json",
            sa.Text(),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_interview_practice_attempts_id",
        "interview_practice_attempts",
        ["id"],
    )
    op.create_index(
        "ix_interview_practice_attempts_user_id",
        "interview_practice_attempts",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_table("interview_practice_attempts")
