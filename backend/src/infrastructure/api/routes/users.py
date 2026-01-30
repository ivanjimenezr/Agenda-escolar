"""
User API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.infrastructure.database import get_db
from src.infrastructure.api.dependencies.auth import get_current_user
from src.domain.models import User
from src.application.schemas.user import UserResponse, UserUpdateRequest
from src.infrastructure.security import get_password_hash, verify_password


router = APIRouter(prefix="/users", tags=["Users"])


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


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current authenticated user information.

    Args:
        user_update: Updated user data
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        UserResponse: Updated user data
    """
    # Update name if provided
    if user_update.name is not None:
        current_user.name = user_update.name

    # Update email if provided
    if user_update.email is not None:
        # Check if email is already taken by another user
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email

    # Update password if provided
    if user_update.current_password and user_update.new_password:
        if not verify_password(user_update.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        current_user.hashed_password = get_password_hash(user_update.new_password)

    db.commit()
    db.refresh(current_user)

    return UserResponse.model_validate(current_user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete current authenticated user account.
    This will also soft-delete all associated student profiles due to cascade.

    Args:
        current_user: Current authenticated user from JWT token
        db: Database session
    """
    # Soft delete the user
    from datetime import datetime
    current_user.deleted_at = datetime.utcnow()
    db.commit()

    return None
