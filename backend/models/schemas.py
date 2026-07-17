from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ==================================================
# AUTH
# ==================================================

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class DeleteAccountRequest(BaseModel):
    password: str


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
