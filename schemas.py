from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from enum import Enum


# --- Enums ---
class AppStatus(str, Enum):
    saved = "saved"
    applied = "applied"
    interview = "interview"
    offer = "offer"
    rejected = "rejected"


# --- User Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# --- Application Schemas ---
class ApplicationCreate(BaseModel):
    company: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., min_length=1, max_length=255)
    status: AppStatus = AppStatus.saved
    applied_date: Optional[date] = None
    job_url: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    location: Optional[str] = None
    job_type: Optional[str] = "full-time"
    notes: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None


class ApplicationUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    status: Optional[AppStatus] = None
    applied_date: Optional[date] = None
    job_url: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    notes: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: UUID
    company: str
    role: str
    status: AppStatus
    applied_date: Optional[date] = None
    job_url: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    notes: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Stats Schema ---
class StatsResponse(BaseModel):
    total: int
    saved: int
    applied: int
    interview: int
    offer: int
    rejected: int
    response_rate: float
    interview_rate: float
