"""
Unit tests for User Use Cases.
Following TDD principles - write tests first, then implement.
"""
import pytest
from sqlalchemy.orm import Session

from src.application.use_cases.user_use_cases import UserUseCases
from src.infrastructure.repositories.user_repository import UserRepository
from src.application.schemas.user import UserRegisterRequest, UserLoginRequest


class TestUserUseCases:
    """Test cases for UserUseCases."""

    def test_register_user_success(self, db_session: Session):
        """Test successful user registration."""
        # Arrange
        repo = UserRepository(db_session)
        use_cases = UserUseCases(repo)
        register_data = UserRegisterRequest(
            email="newuser@example.com",
            password="SecurePass123!",
            name="New User"
        )

        # Act
        user = use_cases.register_user(register_data)

        # Assert
        assert user is not None
        assert user.email == register_data.email
        assert user.name == register_data.name
        assert user.is_active is True
        assert user.email_verified is False
        # Password should be hashed (not plain text)
        assert user.password_hash != register_data.password
        assert len(user.password_hash) > 20  # Bcrypt hash is long

    def test_register_user_duplicate_email_raises_error(self, db_session: Session, sample_user_data):
        """Test registering with duplicate email raises ValueError."""
        # Arrange
        repo = UserRepository(db_session)
        use_cases = UserUseCases(repo)

        # Create first user
        first_user = UserRegisterRequest(
            email=sample_user_data["email"],
            password=sample_user_data["password"],
            name=sample_user_data["name"]
        )
        use_cases.register_user(first_user)

        # Try to create duplicate
        duplicate_user = UserRegisterRequest(
            email=sample_user_data["email"],  # Same email
            password="AnotherPass123!",
            name="Another User"
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Email already registered"):
            use_cases.register_user(duplicate_user)

    def test_login_user_success(self, db_session: Session, sample_user_data):
        """Test successful user login."""
        # Arrange
        repo = UserRepository(db_session)
        use_cases = UserUseCases(repo)

        # Register user first
        register_data = UserRegisterRequest(
            email=sample_user_data["email"],
            password=sample_user_data["password"],
            name=sample_user_data["name"]
        )
        use_cases.register_user(register_data)

        # Login
        login_data = UserLoginRequest(
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )

        # Act
        result = use_cases.login_user(login_data)

        # Assert
        assert result is not None
        assert "user" in result
        assert "access_token" in result
        assert result["user"].email == sample_user_data["email"]
        assert result["access_token"] is not None
        assert len(result["access_token"]) > 20  # JWT token is long

    def test_login_user_wrong_password(self, db_session: Session, sample_user_data):
        """Test login with wrong password raises ValueError."""
        # Arrange
        repo = UserRepository(db_session)
        use_cases = UserUseCases(repo)

        # Register user
        register_data = UserRegisterRequest(
            email=sample_user_data["email"],
            password=sample_user_data["password"],
            name=sample_user_data["name"]
        )
        use_cases.register_user(register_data)

        # Try login with wrong password
        login_data = UserLoginRequest(
            email=sample_user_data["email"],
            password="WrongPassword123!"
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email or password"):
            use_cases.login_user(login_data)

    def test_login_user_non_existing_email(self, db_session: Session):
        """Test login with non-existing email raises ValueError."""
        # Arrange
        repo = UserRepository(db_session)
        use_cases = UserUseCases(repo)

        login_data = UserLoginRequest(
            email="nonexistent@example.com",
            password="SomePassword123!"
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email or password"):
            use_cases.login_user(login_data)

    def test_login_inactive_user_raises_error(self, db_session: Session, sample_user_data):
        """Test login with inactive user raises ValueError."""
        # Arrange
        repo = UserRepository(db_session)
        use_cases = UserUseCases(repo)

        # Register user
        register_data = UserRegisterRequest(
            email=sample_user_data["email"],
            password=sample_user_data["password"],
            name=sample_user_data["name"]
        )
        user = use_cases.register_user(register_data)

        # Deactivate user
        repo.update(user.id, is_active=False)

        # Try to login
        login_data = UserLoginRequest(
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Account is inactive"):
            use_cases.login_user(login_data)

    def test_get_user_by_id_success(self, db_session: Session, sample_user_data):
        """Test retrieving user by ID."""
        # Arrange
        repo = UserRepository(db_session)
        use_cases = UserUseCases(repo)

        # Register user
        register_data = UserRegisterRequest(
            email=sample_user_data["email"],
            password=sample_user_data["password"],
            name=sample_user_data["name"]
        )
        created_user = use_cases.register_user(register_data)

        # Act
        retrieved_user = use_cases.get_user_by_id(created_user.id)

        # Assert
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email

    def test_get_user_by_id_not_found(self, db_session: Session):
        """Test retrieving non-existing user by ID raises ValueError."""
        # Arrange
        repo = UserRepository(db_session)
        use_cases = UserUseCases(repo)
        from uuid import UUID
        fake_uuid = UUID("00000000-0000-0000-0000-000000000000")

        # Act & Assert
        with pytest.raises(ValueError, match="User not found"):
            use_cases.get_user_by_id(fake_uuid)
