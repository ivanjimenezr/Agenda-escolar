"""
User schemas - Pydantic models for user-related operations.
"""

import datetime as dt
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ================ REQUEST SCHEMAS ================


class UserRegisterRequest(BaseModel):
    """Schema for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="User password (min 8 characters)")
    name: str = Field(..., min_length=1, max_length=255, description="User full name")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "padre@example.com", "password": "SecurePass123!", "name": "Juan Pérez"}
        }
    )


class UserLoginRequest(BaseModel):
    """Schema for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    model_config = ConfigDict(
        json_schema_extra={"example": {"email": "padre@example.com", "password": "SecurePass123!"}}
    )


class UserUpdateRequest(BaseModel):
    """Schema for updating user information."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="User full name")
    email: Optional[EmailStr] = Field(None, description="User email address")
    current_password: Optional[str] = Field(None, description="Current password (required if changing password)")
    new_password: Optional[str] = Field(
        None, min_length=8, max_length=100, description="New password (min 8 characters)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Juan Pérez García",
                "email": "nuevo_email@example.com",
                "current_password": "OldPass123!",
                "new_password": "NewPass123!",
            }
        }
    )


class PasswordChangeRequest(BaseModel):
    """Schema for changing user password."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password (min 8 characters)")

    model_config = ConfigDict(
        json_schema_extra={"example": {"current_password": "OldPass123!", "new_password": "NewSecurePass456!"}}
    )


# ================ RESPONSE SCHEMAS ================


class UserResponse(BaseModel):
    """Schema for user response (matches frontend User interface)."""

    id: UUID
    email: str
    name: str
    is_active: bool
    email_verified: bool
    created_at: dt.datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "padre@example.com",
                "name": "Juan Pérez",
                "is_active": True,
                "email_verified": False,
                "created_at": "2026-01-30T14:30:00Z",
            }
        },
    )


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "padre@example.com",
                    "name": "Juan Pérez",
                    "is_active": True,
                    "email_verified": False,
                    "created_at": "2026-01-30T14:30:00Z",
                },
            }
        }
    )


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str

    model_config = ConfigDict(json_schema_extra={"example": {"message": "Operation successful"}})
