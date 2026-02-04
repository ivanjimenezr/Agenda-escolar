"""
Event Schemas

Pydantic schemas for school event request/response validation
"""

import datetime as dt
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ==================== REQUEST SCHEMAS ====================

class EventCreateRequest(BaseModel):
    """Schema for creating a new school event"""
    date: dt.date
    name: str = Field(..., min_length=1, max_length=255)
    type: Literal["Festivo", "Lectivo", "Vacaciones"]

    @field_validator('date', mode='before')
    @classmethod
    def parse_date(cls, v):
        """Convert date string to date object if needed"""
        if isinstance(v, dt.date):
            return v
        if isinstance(v, str):
            # Parse "YYYY-MM-DD" format
            return dt.datetime.strptime(v, "%Y-%m-%d").date()
        return v


class EventUpdateRequest(BaseModel):
    """Schema for updating an existing school event"""
    date: dt.date | None = None
    name: str | None = Field(None, min_length=1, max_length=255)
    type: Literal["Festivo", "Lectivo", "Vacaciones"] | None = None

    @field_validator('date', mode='before')
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


# ==================== RESPONSE SCHEMAS ====================

class EventResponse(BaseModel):
    """Schema for school event response"""
    id: UUID
    user_id: UUID
    date: dt.date
    name: str
    type: str  # "Festivo" | "Lectivo" | "Vacaciones"
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = ConfigDict(from_attributes=True, extra='ignore')
