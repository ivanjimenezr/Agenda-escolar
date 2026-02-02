"""
Subject Schemas

Pydantic schemas for subject request/response validation
"""

from datetime import time, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain.models import SubjectType


# ==================== REQUEST SCHEMAS ====================

class SubjectCreateRequest(BaseModel):
    """Schema for creating a new subject"""
    # student_id can be omitted in the request - it will be filled from the path
    student_id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=255)
    days: List[str] = Field(..., min_length=1)  # Changed from Weekday enum to str
    time: time
    teacher: Optional[str] = Field(None, max_length=255)
    color: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")
    type: SubjectType

    @field_validator('days')
    @classmethod
    def validate_days(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one day must be specified')
        return v

    @field_validator('teacher', mode='before')
    @classmethod
    def empty_teacher_to_none(cls, v):
        # Convert empty string to None so it doesn't fail "min length" checks
        if isinstance(v, str) and v.strip() == '':
            return None
        return v


class SubjectUpdateRequest(BaseModel):
    """Schema for updating an existing subject"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    days: Optional[List[str]] = Field(None, min_length=1)  # Changed from Weekday enum to str
    time: Optional[time] = None
    teacher: Optional[str] = Field(None, max_length=255)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    type: Optional[SubjectType] = None

    @field_validator('days')
    @classmethod
    def validate_days(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError('At least one day must be specified')
        return v


# ==================== RESPONSE SCHEMAS ====================

class SubjectResponse(BaseModel):
    """Schema for subject response"""
    id: UUID
    student_id: UUID
    name: str
    days: List[str]  # Changed from Weekday enum to str
    time: time
    teacher: Optional[str]
    color: str
    type: SubjectType
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
