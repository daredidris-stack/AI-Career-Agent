"""Add append-only administrator audit events."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260729_0012"
down_revision: Union[str, None] = "20260729_0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admin_audit_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=False),
        sa.Column("actor_email", sa.String(length=320), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("target_type", sa.String(length=100), nullable=False),
        sa.Column("target_id", sa.String(length=100), nullable=True),
        sa.Column("request_id", sa.String(length=64), nullable=True),
        sa.Column(
            "details_json",
            sa.Text(),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "id",
        "actor_user_id",
        "action",
        "request_id",
        "created_at",
    ):
        op.create_index(
            f"ix_admin_audit_events_{column}",
            "admin_audit_events",
            [column],
        )

    dialect = op.get_bind().dialect.name
    if dialect == "sqlite":
        op.execute(
            """
            CREATE TRIGGER admin_audit_events_no_update
            BEFORE UPDATE ON admin_audit_events
            BEGIN
                SELECT RAISE(ABORT, 'admin audit events are append-only');
            END
            """
        )
        op.execute(
            """
            CREATE TRIGGER admin_audit_events_no_delete
            BEFORE DELETE ON admin_audit_events
            BEGIN
                SELECT RAISE(ABORT, 'admin audit events are append-only');
            END
            """
        )
    elif dialect == "postgresql":
        op.execute(
            """
            CREATE FUNCTION reject_admin_audit_mutation()
            RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'admin audit events are append-only';
            END;
            $$ LANGUAGE plpgsql
            """
        )
        op.execute(
            """
            CREATE TRIGGER admin_audit_events_append_only
            BEFORE UPDATE OR DELETE ON admin_audit_events
            FOR EACH ROW EXECUTE FUNCTION reject_admin_audit_mutation()
            """
        )


def downgrade() -> None:
    dialect = op.get_bind().dialect.name
    if dialect == "sqlite":
        op.execute("DROP TRIGGER IF EXISTS admin_audit_events_no_update")
        op.execute("DROP TRIGGER IF EXISTS admin_audit_events_no_delete")
    elif dialect == "postgresql":
        op.execute(
            "DROP TRIGGER IF EXISTS admin_audit_events_append_only "
            "ON admin_audit_events"
        )
        op.execute("DROP FUNCTION IF EXISTS reject_admin_audit_mutation()")
    op.drop_table("admin_audit_events")
