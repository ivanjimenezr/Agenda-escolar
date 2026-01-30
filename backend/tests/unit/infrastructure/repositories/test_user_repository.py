"""
Unit tests for User Repository.
Following TDD principles - write tests first, then implement.
"""
import pytest
from uuid import UUID
from sqlalchemy.orm import Session

from src.domain.models import User
from src.infrastructure.repositories.user_repository import UserRepository


class TestUserRepository:
    """Test cases for UserRepository."""

    def test_create_user_success(self, db_session: Session, sample_user_data):
        """Test creating a new user successfully."""
        # Arrange
        repo = UserRepository(db_session)
        email = sample_user_data["email"]
        name = sample_user_data["name"]
        password_hash = sample_user_data["password_hash"]

        # Act
        user = repo.create(email=email, name=name, password_hash=password_hash)

        # Assert
        assert user is not None
        assert user.id is not None
        assert isinstance(user.id, UUID)
        assert user.email == email
        assert user.name == name
        assert user.password_hash == password_hash
        assert user.is_active is True
        assert user.email_verified is False
        assert user.created_at is not None
        assert user.deleted_at is None

    def test_get_by_id_existing_user(self, db_session: Session, sample_user_data):
        """Test retrieving a user by ID."""
        # Arrange
        repo = UserRepository(db_session)
        created_user = repo.create(
            email=sample_user_data["email"],
            name=sample_user_data["name"],
            password_hash=sample_user_data["password_hash"]
        )

        # Act
        retrieved_user = repo.get_by_id(created_user.id)

        # Assert
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email

    def test_get_by_id_non_existing_user(self, db_session: Session):
        """Test retrieving a non-existing user by ID returns None."""
        # Arrange
        repo = UserRepository(db_session)
        fake_uuid = UUID("00000000-0000-0000-0000-000000000000")

        # Act
        user = repo.get_by_id(fake_uuid)

        # Assert
        assert user is None

    def test_get_by_email_existing_user(self, db_session: Session, sample_user_data):
        """Test retrieving a user by email."""
        # Arrange
        repo = UserRepository(db_session)
        created_user = repo.create(
            email=sample_user_data["email"],
            name=sample_user_data["name"],
            password_hash=sample_user_data["password_hash"]
        )

        # Act
        retrieved_user = repo.get_by_email(sample_user_data["email"])

        # Assert
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == sample_user_data["email"]

    def test_get_by_email_non_existing_user(self, db_session: Session):
        """Test retrieving a non-existing user by email returns None."""
        # Arrange
        repo = UserRepository(db_session)

        # Act
        user = repo.get_by_email("nonexistent@example.com")

        # Assert
        assert user is None

    def test_get_by_email_excludes_soft_deleted(self, db_session: Session, sample_user_data):
        """Test that soft-deleted users are not retrieved by email."""
        # Arrange
        repo = UserRepository(db_session)
        user = repo.create(
            email=sample_user_data["email"],
            name=sample_user_data["name"],
            password_hash=sample_user_data["password_hash"]
        )
        # Soft delete the user
        repo.delete(user.id)

        # Act
        retrieved_user = repo.get_by_email(sample_user_data["email"])

        # Assert
        assert retrieved_user is None

    def test_update_user_success(self, db_session: Session, sample_user_data):
        """Test updating user information."""
        # Arrange
        repo = UserRepository(db_session)
        user = repo.create(
            email=sample_user_data["email"],
            name=sample_user_data["name"],
            password_hash=sample_user_data["password_hash"]
        )
        new_name = "Updated Name"
        new_email = "updated@example.com"

        # Act
        updated_user = repo.update(user.id, name=new_name, email=new_email)

        # Assert
        assert updated_user is not None
        assert updated_user.name == new_name
        assert updated_user.email == new_email
        assert updated_user.updated_at > updated_user.created_at

    def test_update_non_existing_user(self, db_session: Session):
        """Test updating a non-existing user returns None."""
        # Arrange
        repo = UserRepository(db_session)
        fake_uuid = UUID("00000000-0000-0000-0000-000000000000")

        # Act
        updated_user = repo.update(fake_uuid, name="New Name")

        # Assert
        assert updated_user is None

    def test_delete_user_soft_delete(self, db_session: Session, sample_user_data):
        """Test soft deleting a user."""
        # Arrange
        repo = UserRepository(db_session)
        user = repo.create(
            email=sample_user_data["email"],
            name=sample_user_data["name"],
            password_hash=sample_user_data["password_hash"]
        )

        # Act
        result = repo.delete(user.id)

        # Assert
        assert result is True
        deleted_user = db_session.query(User).filter(User.id == user.id).first()
        assert deleted_user is not None
        assert deleted_user.deleted_at is not None

    def test_delete_non_existing_user(self, db_session: Session):
        """Test deleting a non-existing user returns False."""
        # Arrange
        repo = UserRepository(db_session)
        fake_uuid = UUID("00000000-0000-0000-0000-000000000000")

        # Act
        result = repo.delete(fake_uuid)

        # Assert
        assert result is False

    def test_exists_by_email_true(self, db_session: Session, sample_user_data):
        """Test checking if a user exists by email (should return True)."""
        # Arrange
        repo = UserRepository(db_session)
        repo.create(
            email=sample_user_data["email"],
            name=sample_user_data["name"],
            password_hash=sample_user_data["password_hash"]
        )

        # Act
        exists = repo.exists_by_email(sample_user_data["email"])

        # Assert
        assert exists is True

    def test_exists_by_email_false(self, db_session: Session):
        """Test checking if a user exists by email (should return False)."""
        # Arrange
        repo = UserRepository(db_session)

        # Act
        exists = repo.exists_by_email("nonexistent@example.com")

        # Assert
        assert exists is False

    def test_exists_by_email_excludes_soft_deleted(self, db_session: Session, sample_user_data):
        """Test that exists_by_email returns False for soft-deleted users."""
        # Arrange
        repo = UserRepository(db_session)
        user = repo.create(
            email=sample_user_data["email"],
            name=sample_user_data["name"],
            password_hash=sample_user_data["password_hash"]
        )
        repo.delete(user.id)

        # Act
        exists = repo.exists_by_email(sample_user_data["email"])

        # Assert
        assert exists is False

    def test_create_user_with_duplicate_email_raises_error(self, db_session: Session, sample_user_data):
        """Test creating a user with duplicate email raises IntegrityError."""
        # Arrange
        repo = UserRepository(db_session)
        repo.create(
            email=sample_user_data["email"],
            name=sample_user_data["name"],
            password_hash=sample_user_data["password_hash"]
        )

        # Act & Assert
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            repo.create(
                email=sample_user_data["email"],  # Same email
                name="Another User",
                password_hash="anotherhash"
            )
