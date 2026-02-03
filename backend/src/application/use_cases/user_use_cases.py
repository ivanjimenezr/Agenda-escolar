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
    UserUpdateRequest,
    PasswordChangeRequest,
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
            update_kwargs['name'] = data.name
        if data.email is not None:
            # Check if email is available
            if data.email != user.email and self.user_repo.exists_by_email(data.email):
                raise ValueError("Email already registered")
            update_kwargs['email'] = data.email

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
