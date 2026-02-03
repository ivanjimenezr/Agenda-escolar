"""
Menu Item Schemas

Pydantic schemas for school menu request/response validation
"""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ==================== REQUEST SCHEMAS ====================

class MenuItemCreateRequest(BaseModel):
    """Schema for creating a new menu item"""
    student_id: UUID
    date: date
    first_course: str = Field(..., min_length=1, max_length=255)
    second_course: str = Field(..., min_length=1, max_length=255)
    side_dish: Optional[str] = Field(None, max_length=255)
    dessert: Optional[str] = Field(None, max_length=255)
    allergens: List[str] = Field(default_factory=list)


class MenuItemUpdateRequest(BaseModel):
    """Schema for updating an existing menu item"""
    date: Optional[date] = None
    first_course: Optional[str] = Field(None, min_length=1, max_length=255)
    second_course: Optional[str] = Field(None, min_length=1, max_length=255)
    side_dish: Optional[str] = Field(None, max_length=255)
    dessert: Optional[str] = Field(None, max_length=255)
    allergens: Optional[List[str]] = None


# ==================== RESPONSE SCHEMAS ====================

class MenuItemResponse(BaseModel):
    """Schema for menu item response"""
    id: UUID
    student_id: UUID
    date: date
    first_course: str
    second_course: str
    side_dish: Optional[str]
    dessert: Optional[str]
    allergens: List[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, extra='ignore')
