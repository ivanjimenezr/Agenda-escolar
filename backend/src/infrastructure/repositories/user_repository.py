"""
User Repository - Data access layer for User entity.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
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

    def get_by_id(self, user_id: UUID | str) -> Optional[User]:
        """
        Get user by ID (excluding soft-deleted users).

        Accepts either a UUID instance or a string. For non-Postgres dialects (eg. SQLite tests)
        compare using the textual representation to avoid Postgres-specific casting in SQL.

        Args:
            user_id: User UUID or string

        Returns:
            Optional[User]: User instance or None if not found
        """
        # Try direct UUID comparison when possible (fast path), but always
        # fall back to a string-based lookup using CAST to avoid DB-specific
        # UUID casting issues observed in unit tests (where the compiled SQL
        # included a Postgres-only ::UUID cast against a SQLite DB).
        from sqlalchemy import cast
        from sqlalchemy import String as SAString
        import uuid as _uuid

        # Fast path: if user_id is a UUID instance, try direct comparison first
        try:
            if isinstance(user_id, _uuid.UUID):
                user = self.db.query(User).filter(
                    User.id == user_id,
                    User.deleted_at.is_(None)
                ).first()
                if user:
                    return user
        except Exception:
            # Be conservative: ignore and fall through to string-based lookup
            pass

        # Fallback: compare the textual representation of the id. This avoids
        # Postgres-specific casting in compiled SQL and works across dialects.
        try:
            lookup_str = str(_uuid.UUID(str(user_id)))
        except Exception:
            lookup_str = str(user_id)

        return self.db.query(User).filter(
            cast(User.id, SAString(36)) == lookup_str,
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

        updated = False
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
                updated = True

        if updated:
            user.updated_at = datetime.now(timezone.utc)

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

        user.deleted_at = datetime.now(timezone.utc)
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
