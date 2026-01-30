"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.infrastructure.database import get_db
from src.infrastructure.repositories.user_repository import UserRepository
from src.application.use_cases.user_use_cases import UserUseCases
from src.application.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
)


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user.

    Args:
        data: User registration data
        db: Database session

    Returns:
        UserResponse: Created user data

    Raises:
        HTTPException 400: If email already exists
    """
    repo = UserRepository(db)
    use_cases = UserUseCases(repo)

    try:
        user = use_cases.register_user(data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
def login_user(
    data: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login user and return JWT token.

    Args:
        data: Login credentials
        db: Database session

    Returns:
        TokenResponse: JWT token and user data

    Raises:
        HTTPException 401: If credentials are invalid
    """
    repo = UserRepository(db)
    use_cases = UserUseCases(repo)

    try:
        result = use_cases.login_user(data)
        return TokenResponse(
            access_token=result["access_token"],
            token_type="bearer",
            user=UserResponse.model_validate(result["user"])
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
