"""Add persistent job listings and ingestion state."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260721_0006"
down_revision: Union[str, None] = "20260720_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "job_listings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dedupe_key", sa.String(length=64), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("source_job_id", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("company", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("listing_url", sa.Text(), nullable=True),
        sa.Column("apply_url", sa.Text(), nullable=True),
        sa.Column("job_type", sa.String(), nullable=True),
        sa.Column("workplace_type", sa.String(), nullable=True),
        sa.Column("skills_json", sa.Text(), server_default="[]", nullable=False),
        sa.Column("salary", sa.String(), nullable=True),
        sa.Column("salary_min", sa.Float(), nullable=True),
        sa.Column("salary_max", sa.Float(), nullable=True),
        sa.Column("salary_currency", sa.String(), nullable=True),
        sa.Column("visa_sponsorship", sa.Boolean(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column(
            "source_metadata_json",
            sa.Text(),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_listings_id", "job_listings", ["id"])
    op.create_index(
        "ix_job_listings_dedupe_key",
        "job_listings",
        ["dedupe_key"],
        unique=True,
    )
    for column in (
        "source",
        "title",
        "company",
        "location",
        "published_at",
        "expires_at",
        "is_active",
        "last_seen_at",
    ):
        op.create_index(
            f"ix_job_listings_{column}",
            "job_listings",
            [column],
        )

    op.create_table(
        "job_sync_states",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sync_key", sa.String(length=64), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("keyword", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("status", sa.String(), server_default="pending", nullable=False),
        sa.Column("last_attempt_at", sa.DateTime(), nullable=True),
        sa.Column("last_success_at", sa.DateTime(), nullable=True),
        sa.Column("next_sync_at", sa.DateTime(), nullable=True),
        sa.Column("jobs_fetched", sa.Integer(), server_default="0", nullable=False),
        sa.Column("jobs_created", sa.Integer(), server_default="0", nullable=False),
        sa.Column("jobs_updated", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_sync_states_id", "job_sync_states", ["id"])
    op.create_index(
        "ix_job_sync_states_sync_key",
        "job_sync_states",
        ["sync_key"],
        unique=True,
    )
    op.create_index(
        "ix_job_sync_states_provider",
        "job_sync_states",
        ["provider"],
    )
    op.create_index(
        "ix_job_sync_states_next_sync_at",
        "job_sync_states",
        ["next_sync_at"],
    )


def downgrade() -> None:
    op.drop_table("job_sync_states")
    op.drop_table("job_listings")
