"""
User Use Cases - Business logic for user operations.
"""
from typing import Dict, Any
from uuid import UUID

from src.domain.models import User
from src.infrastructure.repositories.user_repository import UserRepository
from src.infrastructure.security.password import hash_password, verify_password
from src.infrastructure.security.jwt import create_access_token
from src.application.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
)


class UserUseCases:
    """Use cases for user-related operations."""

    def __init__(self, user_repository: UserRepository):
        """
        Initialize use cases with repository.

        Args:
            user_repository: Repository for user data access
        """
        self.user_repo = user_repository

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
        user = self.user_repo.create(
            email=data.email,
            name=data.name,
            password_hash=password_hash
        )

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

        # Generate JWT token
        access_token = create_access_token(data={"sub": str(user.id)})

        return {
            "user": user,
            "access_token": access_token
        }

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

    def update_user(self, user_id: UUID, **kwargs) -> User:
        """
        Update user information.

        Args:
            user_id: User UUID
            **kwargs: Fields to update

        Returns:
            User: Updated user instance

        Raises:
            ValueError: If user not found or email already taken
        """
        # Check if user exists
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        # If updating email, check if it's available
        if "email" in kwargs and kwargs["email"] != user.email:
            if self.user_repo.exists_by_email(kwargs["email"]):
                raise ValueError("Email already taken")

        # Update user
        updated_user = self.user_repo.update(user_id, **kwargs)

        return updated_user

    def change_password(self, user_id: UUID, current_password: str, new_password: str) -> User:
        """
        Change user password.

        Args:
            user_id: User UUID
            current_password: Current password for verification
            new_password: New password to set

        Returns:
            User: Updated user instance

        Raises:
            ValueError: If user not found or current password is incorrect
        """
        # Get user
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")

        # Hash new password
        new_password_hash = hash_password(new_password)

        # Update password
        updated_user = self.user_repo.update(user_id, password_hash=new_password_hash)

        return updated_user

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
