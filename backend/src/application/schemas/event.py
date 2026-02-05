"""
Event Schemas

Pydantic schemas for school event request/response validation
"""

import datetime as dt
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ==================== REQUEST SCHEMAS ====================


class EventCreateRequest(BaseModel):
    """Schema for creating a new school event"""

    date: dt.date
    time: Optional[dt.time] = None
    name: str = Field(..., min_length=1, max_length=255)
    type: Literal["Festivo", "Lectivo", "Vacaciones"]
    description: Optional[str] = Field(None, max_length=1000)

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

    @field_validator("time", mode="before")
    @classmethod
    def parse_time(cls, v):
        """Convert time string to time object if needed"""
        if v is None or v == "":
            return None
        if isinstance(v, dt.time):
            return v
        if isinstance(v, str):
            # Parse "HH:MM" or "HH:MM:SS" format
            try:
                return dt.datetime.strptime(v, "%H:%M").time()
            except ValueError:
                return dt.datetime.strptime(v, "%H:%M:%S").time()
        return v


class EventUpdateRequest(BaseModel):
    """Schema for updating an existing school event"""

    date: dt.date | None = None
    time: Optional[dt.time] = ...  # Use Ellipsis to distinguish "not provided" from "set to None"
    name: str | None = Field(None, min_length=1, max_length=255)
    type: Literal["Festivo", "Lectivo", "Vacaciones"] | None = None
    description: Optional[str] = Field(..., max_length=1000)

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

    @field_validator("time", mode="before")
    @classmethod
    def parse_time(cls, v):
        """Convert time string to time object if needed"""
        if v is None or v is ... or v == "":
            return v
        if isinstance(v, dt.time):
            return v
        if isinstance(v, str):
            # Parse "HH:MM" or "HH:MM:SS" format
            try:
                return dt.datetime.strptime(v, "%H:%M").time()
            except ValueError:
                return dt.datetime.strptime(v, "%H:%M:%S").time()
        return v


# ==================== RESPONSE SCHEMAS ====================


class EventResponse(BaseModel):
    """Schema for school event response"""

    id: UUID
    user_id: UUID
    date: dt.date
    time: Optional[dt.time] = None
    name: str
    type: str  # "Festivo" | "Lectivo" | "Vacaciones"
    description: Optional[str] = None
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = ConfigDict(from_attributes=True, extra="ignore")
