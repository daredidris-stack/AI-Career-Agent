"""Add saved jobs and saved searches."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260729_0008"
down_revision: Union[str, None] = "20260728_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "saved_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("job_key", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("company", sa.String(length=300), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("source_job_id", sa.String(length=300), nullable=True),
        sa.Column("location", sa.String(length=500), nullable=True),
        sa.Column("listing_url", sa.Text(), nullable=True),
        sa.Column("apply_url", sa.Text(), nullable=True),
        sa.Column(
            "job_data_json",
            sa.Text(),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "job_key",
            name="uq_saved_jobs_user_job_key",
        ),
    )
    op.create_index("ix_saved_jobs_id", "saved_jobs", ["id"])
    op.create_index("ix_saved_jobs_user_id", "saved_jobs", ["user_id"])
    op.create_index("ix_saved_jobs_job_key", "saved_jobs", ["job_key"])

    op.create_table(
        "saved_searches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column(
            "filters_json",
            sa.Text(),
            server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "seen_job_keys_json",
            sa.Text(),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "new_match_count",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "last_result_count",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column("last_run_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_saved_searches_id", "saved_searches", ["id"])
    op.create_index(
        "ix_saved_searches_user_id",
        "saved_searches",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_table("saved_searches")
    op.drop_table("saved_jobs")
