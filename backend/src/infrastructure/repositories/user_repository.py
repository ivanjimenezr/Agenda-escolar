"""
User Repository - Data access layer for User entity.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.domain.models import User


class UserRepository:
    """Repository for User entity operations."""

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create(self, email: str, name: str, password_hash: str) -> User:
        """
        Create a new user.

        Args:
            email: User email address
            name: User full name
            password_hash: Hashed password

        Returns:
            User: Created user instance

        Raises:
            IntegrityError: If email already exists
        """
        user = User(
            email=email,
            name=name,
            password_hash=password_hash,
            is_active=True,
            email_verified=False
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Get user by ID (excluding soft-deleted users).

        Args:
            user_id: User UUID

        Returns:
            Optional[User]: User instance or None if not found
        """
        return self.db.query(User).filter(
            User.id == user_id,
            User.deleted_at.is_(None)
        ).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email (excluding soft-deleted users).

        Args:
            email: User email address

        Returns:
            Optional[User]: User instance or None if not found
        """
        return self.db.query(User).filter(
            User.email == email,
            User.deleted_at.is_(None)
        ).first()

    def update(self, user_id: UUID, **kwargs) -> Optional[User]:
        """
        Update user information.

        Args:
            user_id: User UUID
            **kwargs: Fields to update (name, email, etc.)

        Returns:
            Optional[User]: Updated user or None if not found
        """
        user = self.get_by_id(user_id)

        if not user:
            return None

        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)

        return user

    def delete(self, user_id: UUID) -> bool:
        """
        Soft delete a user by setting deleted_at timestamp.

        Args:
            user_id: User UUID

        Returns:
            bool: True if deleted, False if user not found
        """
        user = self.get_by_id(user_id)

        if not user:
            return False

        user.deleted_at = datetime.utcnow()
        self.db.commit()

        return True

    def exists_by_email(self, email: str) -> bool:
        """
        Check if a user with the given email exists (excluding soft-deleted).

        Args:
            email: User email address

        Returns:
            bool: True if exists, False otherwise
        """
        return self.db.query(User).filter(
            User.email == email,
            User.deleted_at.is_(None)
        ).count() > 0
