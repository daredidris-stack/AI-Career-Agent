"""Add opt-in saved-search email alerts and delivery history."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260729_0011"
down_revision: Union[str, None] = "20260729_0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("saved_searches") as batch:
        batch.add_column(sa.Column(
            "email_alerts_enabled",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ))
        batch.add_column(sa.Column(
            "alert_frequency",
            sa.String(length=20),
            server_default="daily",
            nullable=False,
        ))
        batch.add_column(sa.Column(
            "alert_timezone",
            sa.String(length=64),
            server_default="UTC",
            nullable=False,
        ))
        batch.add_column(sa.Column(
            "next_alert_at",
            sa.DateTime(),
            nullable=True,
        ))
        batch.add_column(sa.Column(
            "last_email_at",
            sa.DateTime(),
            nullable=True,
        ))
        batch.create_index(
            "ix_saved_searches_next_alert_at",
            ["next_alert_at"],
        )

    op.create_table(
        "job_alert_deliveries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("saved_search_id", sa.Integer(), nullable=False),
        sa.Column("batch_key", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column(
            "match_count",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["saved_search_id"],
            ["saved_searches.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "saved_search_id",
            "batch_key",
            name="uq_job_alert_deliveries_search_batch",
        ),
    )
    op.create_index(
        "ix_job_alert_deliveries_id",
        "job_alert_deliveries",
        ["id"],
    )
    op.create_index(
        "ix_job_alert_deliveries_user_id",
        "job_alert_deliveries",
        ["user_id"],
    )
    op.create_index(
        "ix_job_alert_deliveries_saved_search_id",
        "job_alert_deliveries",
        ["saved_search_id"],
    )
    op.create_index(
        "ix_job_alert_deliveries_status",
        "job_alert_deliveries",
        ["status"],
    )


def downgrade() -> None:
    op.drop_table("job_alert_deliveries")
    with op.batch_alter_table("saved_searches") as batch:
        batch.drop_index("ix_saved_searches_next_alert_at")
        batch.drop_column("last_email_at")
        batch.drop_column("next_alert_at")
        batch.drop_column("alert_timezone")
        batch.drop_column("alert_frequency")
        batch.drop_column("email_alerts_enabled")
