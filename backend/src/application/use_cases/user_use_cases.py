"""
User Use Cases - Business logic for user operations.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID

logger = logging.getLogger(__name__)

from src.application.schemas.user import (
    PasswordChangeRequest,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    UserUpdateRequest,
)
from src.domain.models import User
from src.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository
from src.infrastructure.repositories.user_repository import UserRepository
from src.infrastructure.security.jwt import create_access_token, generate_refresh_token, hash_refresh_token
from src.infrastructure.security.password import hash_password, verify_password


class UserUseCases:
    """Use cases for user-related operations."""

    def __init__(self, user_repository: UserRepository, refresh_token_repository: Optional[RefreshTokenRepository] = None):
        """
        Initialize use cases with repository.

        Args:
            user_repository: Repository for user data access
            refresh_token_repository: Optional repository for refresh token data access
        """
        self.user_repo = user_repository
        self.refresh_token_repo = refresh_token_repository

    def register_user(self, data: UserRegisterRequest) -> User:
        """
        Register a new user.

        Args:
            data: User registration data

        Returns:
            User: Created user instance

        Raises:
            ValueError: If email already exists
        """
        # Check if email already exists
        if self.user_repo.exists_by_email(data.email):
            raise ValueError("Email already registered")

        # Hash the password
        password_hash = hash_password(data.password)

        # Create user
        user = self.user_repo.create(email=data.email, name=data.name, password_hash=password_hash)

        return user

    def login_user(self, data: UserLoginRequest) -> Dict[str, Any]:
        """
        Authenticate a user and generate access token.

        Args:
            data: User login credentials

        Returns:
            Dict: Contains 'user' and 'access_token'

        Raises:
            ValueError: If credentials are invalid or account is inactive
        """
        # Get user by email
        user = self.user_repo.get_by_email(data.email)

        if not user:
            raise ValueError("Invalid email or password")

        # Verify password
        if not verify_password(data.password, user.password_hash):
            raise ValueError("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            raise ValueError("Account is inactive")

        # Generate JWT access token
        access_token = create_access_token(data={"sub": str(user.id)})

        # Generate opaque refresh token and persist its hash
        raw_refresh, token_hash, expires_at = generate_refresh_token()
        if self.refresh_token_repo is not None:
            try:
                # Clean up old expired tokens to keep the table lean
                self.refresh_token_repo.delete_expired(user.id)
                self.refresh_token_repo.create(user_id=user.id, token_hash=token_hash, expires_at=expires_at)
            except Exception as exc:
                # If the refresh_tokens table does not exist yet (migration not applied)
                # or any other DB error, log a warning and continue without refresh token.
                # This prevents an unhandled SQLAlchemy exception from reaching Starlette's
                # ServerErrorMiddleware (which sits outside CORSMiddleware), which would
                # produce a 500 response without CORS headers, causing a browser CORS error.
                logger.warning("Could not persist refresh token (migration not applied?): %s", exc)
                try:
                    self.refresh_token_repo.db.rollback()
                except Exception:
                    pass
                raw_refresh = None

        return {"user": user, "access_token": access_token, "refresh_token": raw_refresh}

    def refresh_access_token(self, raw_refresh_token: str) -> Dict[str, Any]:
        """
        Rotate a refresh token: validate the presented token, revoke it,
        issue a new access token and a new refresh token.

        Security: if the presented token is already revoked (reuse detected),
        ALL refresh tokens for the owner are revoked to protect against
        token theft.

        Args:
            raw_refresh_token: Raw opaque refresh token from the client

        Returns:
            Dict with 'access_token' and 'refresh_token'

        Raises:
            ValueError: If the token is invalid, expired, or already revoked
        """
        if self.refresh_token_repo is None:
            raise ValueError("Refresh token repository not configured")

        token_hash = hash_refresh_token(raw_refresh_token)
        stored = self.refresh_token_repo.get_by_hash(token_hash)

        if stored is None:
            raise ValueError("Invalid refresh token")

        # Reuse detection: if already revoked, invalidate ALL sessions
        if stored.is_revoked:
            self.refresh_token_repo.revoke_all_for_user(stored.user_id)
            raise ValueError("Refresh token has already been used. All sessions have been revoked.")

        # Check expiry
        now = datetime.now(timezone.utc)
        # expires_at may be naive (SQLite) or aware (PostgreSQL) – normalise
        expires_at = stored.expires_at
        if expires_at.tzinfo is None:
            from datetime import timezone as _tz
            expires_at = expires_at.replace(tzinfo=_tz.utc)
        if now > expires_at:
            self.refresh_token_repo.revoke(stored)
            raise ValueError("Refresh token has expired")

        # Validate the user still exists and is active
        user = self.user_repo.get_by_id(stored.user_id)
        if user is None or not user.is_active:
            self.refresh_token_repo.revoke(stored)
            raise ValueError("User account not found or inactive")

        # Revoke the used token (rotation: one-time use)
        self.refresh_token_repo.revoke(stored)

        # Issue new tokens
        new_access_token = create_access_token(data={"sub": str(user.id)})
        new_raw_refresh, new_token_hash, new_expires_at = generate_refresh_token()
        self.refresh_token_repo.create(user_id=user.id, token_hash=new_token_hash, expires_at=new_expires_at)

        return {"user": user, "access_token": new_access_token, "refresh_token": new_raw_refresh}

    def logout_user(self, raw_refresh_token: str) -> bool:
        """
        Revoke a refresh token to log the user out of a specific session.

        Args:
            raw_refresh_token: Raw opaque refresh token from the client

        Returns:
            bool: True if the token was found and revoked

        Raises:
            ValueError: If token is not found
        """
        if self.refresh_token_repo is None:
            raise ValueError("Refresh token repository not configured")

        token_hash = hash_refresh_token(raw_refresh_token)
        stored = self.refresh_token_repo.get_by_hash(token_hash)

        if stored is None:
            raise ValueError("Invalid refresh token")

        if not stored.is_revoked:
            self.refresh_token_repo.revoke(stored)

        return True

    def get_user_by_id(self, user_id: UUID) -> User:
        """
        Get user by ID.

        Args:
            user_id: User UUID

        Returns:
            User: User instance

        Raises:
            ValueError: If user not found
        """
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        return user

    def update_user(self, user_id: UUID, data: UserUpdateRequest) -> User:
        """
        Update user information.

        Args:
            user_id: User UUID
            data: User update data

        Returns:
            User: Updated user instance

        Raises:
            ValueError: If user not found, email already taken, or password validation fails
        """
        # Check if user exists
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        # Handle password change if both passwords provided
        if data.current_password and data.new_password:
            # Verify current password
            if not verify_password(data.current_password, user.password_hash):
                raise ValueError("Current password is incorrect")
            # Hash and update password
            password_hash = hash_password(data.new_password)
            self.user_repo.update(user_id, password_hash=password_hash)
        elif data.current_password or data.new_password:
            # One provided but not both
            raise ValueError("Both current_password and new_password are required")

        # Build update kwargs for other fields
        update_kwargs = {}
        if data.name is not None:
            update_kwargs["name"] = data.name
        if data.email is not None:
            # Check if email is available
            if data.email != user.email and self.user_repo.exists_by_email(data.email):
                raise ValueError("Email already registered")
            update_kwargs["email"] = data.email

        # Update user if there are changes
        if update_kwargs:
            updated_user = self.user_repo.update(user_id, **update_kwargs)
            return updated_user

        return user

    def change_password(self, user_id: UUID, data: PasswordChangeRequest) -> bool:
        """
        Change user password.

        Args:
            user_id: User UUID
            data: Password change data

        Returns:
            bool: True if successful

        Raises:
            ValueError: If user not found or current password is incorrect
        """
        # Get user
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        # Verify current password
        if not verify_password(data.current_password, user.password_hash):
            raise ValueError("Current password is incorrect")

        # Hash new password
        new_password_hash = hash_password(data.new_password)

        # Update password
        self.user_repo.update(user_id, password_hash=new_password_hash)

        return True

    def delete_user(self, user_id: UUID) -> bool:
        """
        Soft delete a user.

        Args:
            user_id: User UUID

        Returns:
            bool: True if deleted

        Raises:
            ValueError: If user not found
        """
        result = self.user_repo.delete(user_id)

        if not result:
            raise ValueError("User not found")

        return result
