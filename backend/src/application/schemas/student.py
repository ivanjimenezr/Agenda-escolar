"""
Student Profile Schemas

Pydantic schemas for student profile request/response validation
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ==================== REQUEST SCHEMAS ====================

class StudentCreateRequest(BaseModel):
    """Schema for creating a new student profile"""
    name: str = Field(..., min_length=1, max_length=255)
    school: str = Field(..., min_length=1, max_length=255)
    grade: str = Field(..., min_length=1, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    allergies: List[str] = Field(default=[])
    excluded_foods: List[str] = Field(default=[])


class StudentUpdateRequest(BaseModel):
    """Schema for updating an existing student profile"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    school: Optional[str] = Field(None, min_length=1, max_length=255)
    grade: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    allergies: Optional[List[str]] = None
    excluded_foods: Optional[List[str]] = None


# ==================== RESPONSE SCHEMAS ====================

class StudentResponse(BaseModel):
    """Schema for student profile response"""
    id: UUID
    user_id: UUID
    name: str
    school: str
    grade: str
    avatar_url: Optional[str]
    allergies: List[str]
    excluded_foods: List[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
