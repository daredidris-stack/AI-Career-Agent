"""Add reviewed application package references."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260728_0007"
down_revision: Union[str, None] = "20260721_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("job_applications") as batch_op:
        batch_op.add_column(sa.Column("source", sa.String(), nullable=True))
        batch_op.add_column(
            sa.Column("source_job_id", sa.String(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("resume_document_id", sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("cover_letter_document_id", sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("package_reviewed_at", sa.DateTime(), nullable=True)
        )
        batch_op.create_foreign_key(
            "fk_job_applications_resume_document_id_career_documents",
            "career_documents",
            ["resume_document_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_foreign_key(
            "fk_job_applications_cover_letter_document_id_career_documents",
            "career_documents",
            ["cover_letter_document_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index(
            "ix_job_applications_resume_document_id",
            ["resume_document_id"],
        )
        batch_op.create_index(
            "ix_job_applications_cover_letter_document_id",
            ["cover_letter_document_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("job_applications") as batch_op:
        batch_op.drop_index(
            "ix_job_applications_cover_letter_document_id"
        )
        batch_op.drop_index("ix_job_applications_resume_document_id")
        batch_op.drop_constraint(
            "fk_job_applications_cover_letter_document_id_career_documents",
            type_="foreignkey",
        )
        batch_op.drop_constraint(
            "fk_job_applications_resume_document_id_career_documents",
            type_="foreignkey",
        )
        batch_op.drop_column("package_reviewed_at")
        batch_op.drop_column("cover_letter_document_id")
        batch_op.drop_column("resume_document_id")
        batch_op.drop_column("source_job_id")
        batch_op.drop_column("source")
