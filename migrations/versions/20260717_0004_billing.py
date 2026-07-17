"""Add customer subscription state."""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "20260717_0004"
down_revision: Union[str, None] = "20260717_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("plan", sa.String(), server_default="free", nullable=False))
        batch.add_column(sa.Column("stripe_customer_id", sa.String(), nullable=True))
        batch.add_column(sa.Column("stripe_subscription_id", sa.String(), nullable=True))
        batch.add_column(sa.Column("subscription_status", sa.String(), nullable=True))
        batch.add_column(sa.Column("subscription_period_end", sa.DateTime(), nullable=True))
        batch.create_unique_constraint("uq_users_stripe_customer_id", ["stripe_customer_id"])
        batch.create_unique_constraint("uq_users_stripe_subscription_id", ["stripe_subscription_id"])

def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_constraint("uq_users_stripe_subscription_id", type_="unique")
        batch.drop_constraint("uq_users_stripe_customer_id", type_="unique")
        for column in ("subscription_period_end", "subscription_status", "stripe_subscription_id", "stripe_customer_id", "plan"):
            batch.drop_column(column)
