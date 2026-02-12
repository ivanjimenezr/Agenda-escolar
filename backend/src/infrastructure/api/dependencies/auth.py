"""
Authentication dependencies for FastAPI endpoints.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.domain.models import User
from src.infrastructure.database import get_db
from src.infrastructure.repositories.user_repository import UserRepository
from src.infrastructure.security.jwt import get_user_id_from_token

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to get current authenticated user from JWT token.

    Uses auto_error=False so that missing credentials raise HTTP 401
    (RFC 9110 §15.5.2) instead of FastAPI's default HTTP 403.

    Args:
        credentials: HTTP Bearer token credentials (None if header absent)
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException 401: If credentials are missing or token is invalid
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Extract user ID from token
    user_id = get_user_id_from_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)

    # Fallback: some test DBs store UUIDs as strings; try string lookup if necessary
    if user is None:
        try:
            user = db.query(User).filter(User.id == str(user_id), User.deleted_at.is_(None)).first()
        except Exception:
            user = None

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user
