"""
Subject Schemas

Pydantic schemas for subject request/response validation
"""

import datetime as dt
from typing import List, Optional, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ==================== REQUEST SCHEMAS ====================

class SubjectCreateRequest(BaseModel):
    """Schema for creating a new subject"""
    # student_id can be omitted in the request - it will be filled from the path
    student_id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=255)
    days: List[str] = Field(..., min_length=1)  # Changed from Weekday enum to str
    time: dt.time
    teacher: Optional[str] = Field(None, max_length=255)
    color: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")
    type: Literal["colegio", "extraescolar"]  # Changed from enum to string literal

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

    @field_validator('time', mode='before')
    @classmethod
    def parse_time(cls, v):
        # Convert time string to time object if needed
        from datetime import time
        # If it's already a time object, return it
        if isinstance(v, dt.time):
            return v
        if isinstance(v, str):
            # Parse "HH:MM:SS" or "HH:MM" format
            parts = v.split(':')
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
            second = int(parts[2]) if len(parts) > 2 else 0
            return dt.time(hour, minute, second)
        return v

    @field_validator('type', mode='before')
    @classmethod
    def normalize_type(cls, v):
        # Convert type to lowercase to handle frontend sending uppercase
        if isinstance(v, str):
            return v.lower()
        return v


class SubjectUpdateRequest(BaseModel):
    """Schema for updating an existing subject"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    days: Optional[List[str]] = Field(None, min_length=1)  # Changed from Weekday enum to str
    time: Optional[dt.time] = None  # Don't use Field() here to avoid recursion
    teacher: Optional[str] = Field(None, max_length=255)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    type: Optional[Literal["colegio", "extraescolar"]] = None  # Changed from enum to string literal

    @field_validator('days')
    @classmethod
    def validate_days(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError('At least one day must be specified')
        return v

    @field_validator('time', mode='before')
    @classmethod
    def parse_time(cls, v):
        # Convert time string to time object if needed
        if v is None:
            return v
        # If it's already a time object, return it
        from datetime import time
        if isinstance(v, dt.time):
            return v
        if isinstance(v, str):
            # Parse "HH:MM:SS" or "HH:MM" format
            parts = v.split(':')
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
            second = int(parts[2]) if len(parts) > 2 else 0
            return dt.time(hour, minute, second)
        return v

    @field_validator('type', mode='before')
    @classmethod
    def normalize_type_update(cls, v):
        # Convert type to lowercase to handle frontend sending uppercase
        if isinstance(v, str):
            return v.lower()
        return v


# ==================== RESPONSE SCHEMAS ====================

class SubjectResponse(BaseModel):
    """Schema for subject response"""
    id: UUID
    student_id: UUID
    name: str
    days: List[str]  # Changed from Weekday enum to str
    time: dt.time
    teacher: Optional[str]
    color: str
    type: str  # Changed from enum to string
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = ConfigDict(from_attributes=True, extra='ignore')
