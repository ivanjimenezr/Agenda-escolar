"""
Dinner Schemas

Pydantic schemas for dinner request/response validation
"""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ==================== REQUEST SCHEMAS ====================

class DinnerGenerateRequest(BaseModel):
    """Schema for generating dinner suggestions with AI"""
    type: str = Field(..., pattern="^(today|week)$", description="Generate for today or full week")
    target_date: Optional[date] = Field(None, description="Specific date for 'today' type (defaults to today)")


class DinnerCreateRequest(BaseModel):
    """Schema for creating a dinner manually"""
    date: date = Field(..., description="Date for the dinner")
    meal: str = Field(..., min_length=1, max_length=500, description="Meal description")
    ingredients: List[str] = Field(default_factory=list, description="List of ingredients")


class DinnerUpdateRequest(BaseModel):
    """Schema for updating an existing dinner"""
    meal: Optional[str] = Field(None, min_length=1, max_length=500)
    ingredients: Optional[List[str]] = None


class ShoppingListRequest(BaseModel):
    """Schema for generating shopping list"""
    scope: str = Field(..., pattern="^(today|week|custom)$", description="Scope for shopping list")
    start_date: Optional[date] = Field(None, description="Start date for custom range")
    end_date: Optional[date] = Field(None, description="End date for custom range")


# ==================== RESPONSE SCHEMAS ====================

class DinnerResponse(BaseModel):
    """Schema for dinner response"""
    id: UUID
    student_id: UUID
    date: date
    meal: str
    ingredients: List[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ShoppingListCategoryResponse(BaseModel):
    """Schema for shopping list category"""
    category: str
    items: List[str]


class ShoppingListResponse(BaseModel):
    """Schema for shopping list response"""
    categories: List[ShoppingListCategoryResponse]
