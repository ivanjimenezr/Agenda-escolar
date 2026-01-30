"""
User API endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.infrastructure.database import get_db
from src.infrastructure.api.dependencies.auth import get_current_user
from src.domain.models import User
from src.application.schemas.user import UserResponse


router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.

    Args:
        current_user: Current authenticated user from JWT token

    Returns:
        UserResponse: Current user data
    """
    return UserResponse.model_validate(current_user)
