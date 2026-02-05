"""
Exam Schemas

Pydantic schemas for exam request/response validation
"""

import datetime as dt
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ==================== REQUEST SCHEMAS ====================


class ExamCreateRequest(BaseModel):
    """Schema for creating a new exam"""

    student_id: Optional[UUID] = None  # Can be omitted - filled from path
    subject: str = Field(..., min_length=1, max_length=255)
    date: dt.date
    topic: str = Field(..., min_length=1)
    notes: Optional[str] = None

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v):
        """Convert date string to date object if needed"""
        if isinstance(v, dt.date):
            return v
        if isinstance(v, str):
            # Parse "YYYY-MM-DD" format
            return dt.datetime.strptime(v, "%Y-%m-%d").date()
        return v

    @field_validator("notes", mode="before")
    @classmethod
    def empty_notes_to_none(cls, v):
        """Convert empty string to None"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class ExamUpdateRequest(BaseModel):
    """Schema for updating an existing exam"""

    subject: Optional[str] = Field(None, min_length=1, max_length=255)
    date: Optional[dt.date] = None
    topic: Optional[str] = Field(None, min_length=1)
    notes: Optional[str] = None

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v):
        """Convert date string to date object if needed"""
        if v is None:
            return v
        if isinstance(v, dt.date):
            return v
        if isinstance(v, str):
            # Parse "YYYY-MM-DD" format
            return dt.datetime.strptime(v, "%Y-%m-%d").date()
        return v

    @field_validator("notes", mode="before")
    @classmethod
    def empty_notes_to_none(cls, v):
        """Convert empty string to None"""
        if v is not None and isinstance(v, str) and v.strip() == "":
            return None
        return v


# ==================== RESPONSE SCHEMAS ====================


class ExamResponse(BaseModel):
    """Schema for exam response"""

    id: UUID
    student_id: UUID
    subject: str
    date: dt.date
    topic: str
    notes: Optional[str]
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = ConfigDict(from_attributes=True, extra="ignore")
