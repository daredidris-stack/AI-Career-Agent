"""Create the initial authenticated career platform schema."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260717_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("token_version", sa.Integer(), server_default="0", nullable=False),
        sa.Column("failed_login_attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("locked_until", sa.DateTime(), nullable=True),
        sa.Column("is_email_verified", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_id", "users", ["id"], unique=False)

    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("state", sa.String(), nullable=True),
        sa.Column("city", sa.String(), nullable=True),
        sa.Column("current_role", sa.String(), nullable=True),
        sa.Column("target_role", sa.String(), nullable=True),
        sa.Column("years_experience", sa.Integer(), nullable=True),
        sa.Column("professional_summary", sa.Text(), nullable=True),
        sa.Column("technical_skills", sa.Text(), nullable=True),
        sa.Column("soft_skills", sa.Text(), nullable=True),
        sa.Column("linkedin", sa.String(), nullable=True),
        sa.Column("github", sa.String(), nullable=True),
        sa.Column("portfolio", sa.String(), nullable=True),
        sa.Column("preferred_job_type", sa.String(), nullable=True),
        sa.Column("preferred_work_mode", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_profiles_id", "profiles", ["id"], unique=False)

    op.create_table(
        "resume_analyses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("resume_score", sa.Integer(), nullable=False),
        sa.Column("ats_score", sa.Integer(), nullable=False),
        sa.Column("strengths", sa.Text(), nullable=False),
        sa.Column("improvements", sa.Text(), nullable=False),
        sa.Column("extracted_skills", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_resume_analyses_id", "resume_analyses", ["id"], unique=False)
    op.create_index("ix_resume_analyses_user_id", "resume_analyses", ["user_id"], unique=False)

    op.create_table(
        "career_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_filename", sa.String(), nullable=True),
        sa.Column("job_description", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_career_documents_id", "career_documents", ["id"], unique=False)
    op.create_index("ix_career_documents_kind", "career_documents", ["kind"], unique=False)
    op.create_index("ix_career_documents_user_id", "career_documents", ["user_id"], unique=False)

    op.create_table(
        "career_document_revisions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["career_documents.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_career_document_revisions_document_id", "career_document_revisions", ["document_id"], unique=False)
    op.create_index("ix_career_document_revisions_id", "career_document_revisions", ["id"], unique=False)
    op.create_index("ix_career_document_revisions_user_id", "career_document_revisions", ["user_id"], unique=False)

    op.create_table(
        "job_applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("company", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("job_url", sa.String(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("contact_name", sa.String(), nullable=True),
        sa.Column("contact_email", sa.String(), nullable=True),
        sa.Column("deadline_at", sa.DateTime(), nullable=True),
        sa.Column("follow_up_at", sa.DateTime(), nullable=True),
        sa.Column("applied_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_applications_id", "job_applications", ["id"], unique=False)
    op.create_index("ix_job_applications_status", "job_applications", ["status"], unique=False)
    op.create_index("ix_job_applications_user_id", "job_applications", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("job_applications")
    op.drop_table("career_document_revisions")
    op.drop_table("career_documents")
    op.drop_table("resume_analyses")
    op.drop_table("profiles")
    op.drop_table("users")
