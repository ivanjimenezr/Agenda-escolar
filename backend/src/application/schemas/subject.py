"""
Subject Schemas

Pydantic schemas for subject request/response validation
"""

from datetime import time, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain.models import SubjectType, Weekday


# ==================== REQUEST SCHEMAS ====================

class SubjectCreateRequest(BaseModel):
    """Schema for creating a new subject"""
    student_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    days: List[Weekday] = Field(..., min_length=1)
    time: time
    teacher: str = Field(..., min_length=1, max_length=255)
    color: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")
    type: SubjectType

    @field_validator('days')
    @classmethod
    def validate_days(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one day must be specified')
        return v


class SubjectUpdateRequest(BaseModel):
    """Schema for updating an existing subject"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    days: Optional[List[Weekday]] = Field(None, min_length=1)
    time: Optional[time] = None
    teacher: Optional[str] = Field(None, min_length=1, max_length=255)
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
    days: List[Weekday]
    time: time
    teacher: str
    color: str
    type: SubjectType
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
