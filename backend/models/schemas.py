from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


# ==================================================
# AUTH
# ==================================================

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    accept_terms: Literal[True]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    turnstile_token: str | None = Field(default=None, max_length=2048)


class GoogleLoginRequest(BaseModel):
    credential: str = Field(min_length=100, max_length=8192)
    accept_terms: Literal[True]


class DeleteAccountRequest(BaseModel):
    password: str


class EmailRequest(BaseModel):
    email: EmailStr


class TokenConfirmationRequest(BaseModel):
    token: str


class PasswordResetRequest(TokenConfirmationRequest):
    new_password: str = Field(min_length=8, max_length=128)


class MessageResponse(BaseModel):
    message: str


class JobDescriptionRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    company: str = Field(default="", max_length=300)
    location: str = Field(default="", max_length=500)
    listing_url: str | None = Field(default=None, max_length=2048)


class JobDescriptionResponse(BaseModel):
    description: str | None = None
    enriched: bool = False


class SavedJobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    company: str = Field(min_length=1, max_length=300)
    source: str | None = Field(default=None, max_length=100)
    source_job_id: str | None = Field(default=None, max_length=300)
    location: str | None = Field(default=None, max_length=500)
    listing_url: str | None = Field(default=None, max_length=2048)
    apply_url: str | None = Field(default=None, max_length=2048)
    description: str | None = Field(default=None, max_length=50000)
    job_type: str | None = Field(default=None, max_length=100)
    workplace_type: str | None = Field(default=None, max_length=100)
    salary: str | None = Field(default=None, max_length=300)
    visa_sponsorship: bool | None = None
    updated: str | None = Field(default=None, max_length=100)
    analysis: dict = Field(default_factory=dict)


class SavedSearchFilters(BaseModel):
    keyword: str = Field(min_length=1, max_length=300)
    country: str = Field(default="Worldwide", max_length=200)
    city: str = Field(default="", max_length=200)
    industry: str = Field(default="", max_length=200)
    work_mode: str = Field(default="", max_length=100)
    employment_type: str = Field(default="", max_length=100)
    posted_within_days: int = Field(default=0, ge=0, le=365)
    min_salary: int = Field(default=0, ge=0)
    min_score: int = Field(default=0, ge=0, le=100)


class SavedSearchCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    filters: SavedSearchFilters


class SavedSearchAlertUpdate(BaseModel):
    enabled: bool
    frequency: Literal["daily", "weekly"] = "daily"
    timezone: str = Field(default="UTC", min_length=1, max_length=64)


class EmailAlertUnsubscribe(BaseModel):
    token: str = Field(min_length=20, max_length=500)


class SupportTicketCreate(BaseModel):
    category: Literal[
        "account",
        "jobs",
        "documents",
        "applications",
        "billing",
        "bug",
        "feedback",
        "other",
    ]
    subject: str = Field(min_length=3, max_length=200)
    message: str = Field(min_length=10, max_length=10000)


class SupportTicketUpdate(BaseModel):
    status: Literal["new", "in_progress", "resolved", "closed"]
    admin_note: str | None = Field(default=None, max_length=10000)


class InterviewPracticeCreate(BaseModel):
    role: str = Field(min_length=1, max_length=200)
    interview_type: str = Field(min_length=1, max_length=100)
    question: str = Field(min_length=5, max_length=2000)
    answer: str = Field(min_length=20, max_length=10000)


class CareerDocumentCreate(BaseModel):
    kind: str
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    source_filename: str | None = None
    job_description: str | None = None
    metadata: dict = Field(default_factory=dict)


class CareerDocumentUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


class CareerDocumentResponse(BaseModel):
    id: int
    user_id: int
    kind: str
    title: str
    content: str
    source_filename: str | None
    job_description: str | None
    metadata_json: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CareerDocumentRevisionResponse(BaseModel):
    id: int
    document_id: int
    title: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class JobApplicationData(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    role: str = Field(min_length=1, max_length=200)
    job_url: str | None = Field(default=None, max_length=2048)
    location: str | None = Field(default=None, max_length=500)
    source: str | None = Field(default=None, max_length=100)
    source_job_id: str | None = Field(default=None, max_length=300)
    resume_document_id: int | None = None
    cover_letter_document_id: int | None = None
    status: str = "saved"
    notes: str | None = None
    contact_name: str | None = None
    contact_email: EmailStr | None = None
    deadline_at: datetime | None = None
    follow_up_at: datetime | None = None
    applied_at: datetime | None = None


class JobApplicationCreate(JobApplicationData):
    pass


class JobApplicationUpdate(JobApplicationData):
    pass


class JobApplicationPrepare(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    role: str = Field(min_length=1, max_length=200)
    job_url: str = Field(min_length=1, max_length=2048)
    location: str | None = Field(default=None, max_length=500)
    source: str | None = Field(default=None, max_length=100)
    source_job_id: str | None = Field(default=None, max_length=300)
    resume_document_id: int
    cover_letter_document_id: int | None = None
    review_confirmed: Literal[True]
    manual_submission_confirmed: Literal[True]


class JobApplicationResponse(JobApplicationData):
    id: int
    user_id: int
    package_reviewed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# ==================================================
# USER
# ==================================================

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime
    is_email_verified: bool = False
    terms_accepted_at: datetime | None = None
    terms_version: str | None = None

    model_config = {
        "from_attributes": True
    }


# ==================================================
# PROFILE
# ==================================================

class ProfileCreate(BaseModel):

    phone: str | None = None

    country: str | None = None
    state: str | None = None
    city: str | None = None

    current_role: str | None = None
    target_role: str | None = None
    years_experience: int | None = None

    professional_summary: str | None = None

    technical_skills: str | None = None
    soft_skills: str | None = None

    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None

    preferred_job_type: str | None = None
    preferred_work_mode: str | None = None


class ProfileResponse(ProfileCreate):

    id: int
    user_id: int

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ProfileAutofillResponse(ProfileCreate):
    extracted_fields: list[str] = Field(default_factory=list)
    target_role_options: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
