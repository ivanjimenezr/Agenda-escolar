"""
Active Modules Schemas

Pydantic schemas for active modules request/response validation
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ==================== REQUEST SCHEMAS ====================

class ActiveModulesUpdateRequest(BaseModel):
    """Schema for updating active modules configuration"""
    subjects: Optional[bool] = None
    exams: Optional[bool] = None
    menu: Optional[bool] = None
    events: Optional[bool] = None
    dinner: Optional[bool] = None
    contacts: Optional[bool] = None


# ==================== RESPONSE SCHEMAS ====================

class ActiveModulesResponse(BaseModel):
    """Schema for active modules response"""
    id: UUID
    student_id: UUID
    subjects: bool
    exams: bool
    menu: bool
    events: bool
    dinner: bool
    contacts: bool

    model_config = ConfigDict(from_attributes=True, extra='ignore')
