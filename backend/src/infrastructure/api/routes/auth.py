"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.application.schemas.user import (
    LogoutRequest,
    MessageResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from src.application.use_cases.user_use_cases import UserUseCases
from src.infrastructure.api.rate_limit import limiter
from src.infrastructure.database import get_db
from src.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository
from src.infrastructure.repositories.user_repository import UserRepository

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


def _build_use_cases(db: Session) -> UserUseCases:
    """Instantiate UserUseCases with both repositories."""
    return UserUseCases(
        user_repository=UserRepository(db),
        refresh_token_repository=RefreshTokenRepository(db),
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
def register_user(request: Request, data: UserRegisterRequest, db: Session = Depends(get_db)):
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
    use_cases = _build_use_cases(db)

    try:
        user = use_cases.register_user(data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login_user(request: Request, data: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Login user and return JWT access token + opaque refresh token.

    The refresh token is valid for 7 days. Use POST /auth/refresh to
    obtain a new access token without re-entering credentials.

    Args:
        data: Login credentials
        db: Database session

    Returns:
        TokenResponse: JWT access token, refresh token and user data

    Raises:
        HTTPException 401: If credentials are invalid
    """
    use_cases = _build_use_cases(db)

    try:
        result = use_cases.login_user(data)
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type="bearer",
            user=UserResponse.model_validate(result["user"]),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Rotate a refresh token to obtain a new access token and a new refresh token.

    Each refresh token can only be used once (token rotation). Presenting a
    previously-used (revoked) token triggers reuse detection: all active
    sessions for the user are invalidated immediately.

    Args:
        data: Body containing the current refresh token
        db: Database session

    Returns:
        TokenResponse: New access token, new refresh token and user data

    Raises:
        HTTPException 401: If the refresh token is invalid, expired, or revoked
    """
    use_cases = _build_use_cases(db)

    try:
        result = use_cases.refresh_access_token(data.refresh_token)
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type="bearer",
            user=UserResponse.model_validate(result["user"]),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout", response_model=MessageResponse)
def logout_user(data: LogoutRequest, db: Session = Depends(get_db)):
    """
    Logout user by revoking the supplied refresh token.

    The access token will expire naturally (30 min). To force immediate
    invalidation of all sessions use DELETE /api/v1/users/me instead.

    Args:
        data: Body containing the refresh token to revoke
        db: Database session

    Returns:
        MessageResponse: Confirmation message

    Raises:
        HTTPException 400: If the refresh token is not recognised
    """
    use_cases = _build_use_cases(db)

    try:
        use_cases.logout_user(data.refresh_token)
        return MessageResponse(message="Successfully logged out")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
