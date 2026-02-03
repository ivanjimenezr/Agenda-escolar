"""
Unit tests for User Update functionality

These tests ensure user profile and password updates work correctly.
"""

import pytest
from sqlalchemy.orm import Session

from src.domain.models import User
from src.infrastructure.repositories.user_repository import UserRepository
from src.application.use_cases.user_use_cases import UserUseCases
from src.application.schemas.user import UserUpdateRequest, PasswordChangeRequest


@pytest.fixture
def sample_user(db_session: Session):
    """Create a sample user for testing"""
    from src.infrastructure.security.password import hash_password
    user = User(
        email="testuserupdate@example.com",
        name="Test User Update",
        password_hash=hash_password("password123")  # Hash password properly
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_use_cases(db_session: Session):
    """Create UserUseCases instance"""
    user_repo = UserRepository(db_session)
    return UserUseCases(user_repo)


class TestUserUpdate:
    """Test suite for user update operations"""

    def test_update_user_name_only(self, db_session: Session, sample_user: User, user_use_cases: UserUseCases):
        """Test updating only the user's name"""
        update_data = UserUpdateRequest(
            name="Updated Name"
        )

        updated = user_use_cases.update_user(
            user_id=sample_user.id,
            data=update_data
        )

        assert updated.name == "Updated Name"
        # Email unchanged
        assert updated.email == "testuserupdate@example.com"

    def test_update_user_email_only(self, db_session: Session, sample_user: User, user_use_cases: UserUseCases):
        """Test updating only the user's email"""
        update_data = UserUpdateRequest(
            email="newemail@example.com"
        )

        updated = user_use_cases.update_user(
            user_id=sample_user.id,
            data=update_data
        )

        assert updated.email == "newemail@example.com"
        # Name unchanged
        assert updated.name == "Test User Update"

    def test_update_user_name_and_email(self, db_session: Session, sample_user: User, user_use_cases: UserUseCases):
        """Test updating both name and email"""
        update_data = UserUpdateRequest(
            name="New Name",
            email="newuser@example.com"
        )

        updated = user_use_cases.update_user(
            user_id=sample_user.id,
            data=update_data
        )

        assert updated.name == "New Name"
        assert updated.email == "newuser@example.com"

    def test_update_user_password_via_update_request(self, db_session: Session, sample_user: User, user_use_cases: UserUseCases):
        """Test updating password through UserUpdateRequest"""
        from src.infrastructure.security.password import verify_password
        old_hash = sample_user.password_hash

        update_data = UserUpdateRequest(
            current_password="password123",
            new_password="NewSecurePassword456"
        )

        updated = user_use_cases.update_user(
            user_id=sample_user.id,
            data=update_data
        )

        # Verify password was changed
        db_session.refresh(sample_user)
        assert sample_user.password_hash != old_hash
        assert verify_password("NewSecurePassword456", sample_user.password_hash)

    def test_update_user_password_wrong_current(self, db_session: Session, sample_user: User, user_use_cases: UserUseCases):
        """Test updating password with wrong current password fails"""
        update_data = UserUpdateRequest(
            current_password="wrongpassword",
            new_password="NewPassword"
        )

        with pytest.raises(ValueError, match="Current password is incorrect"):
            user_use_cases.update_user(
                user_id=sample_user.id,
                data=update_data
            )

    def test_update_user_password_too_short(self, db_session: Session, sample_user: User):
        """Test password validation - too short"""
        with pytest.raises(ValueError):
            UserUpdateRequest(
                current_password="password123",
                new_password="short"  # Less than 8 characters
            )

    def test_update_user_all_fields(self, db_session: Session, sample_user: User, user_use_cases: UserUseCases):
        """Test updating all fields at once"""
        from src.infrastructure.security.password import verify_password
        old_hash = sample_user.password_hash

        update_data = UserUpdateRequest(
            name="Completely New Name",
            email="completelynew@example.com",
            current_password="password123",
            new_password="BrandNewPass789"
        )

        updated = user_use_cases.update_user(
            user_id=sample_user.id,
            data=update_data
        )

        assert updated.name == "Completely New Name"
        assert updated.email == "completelynew@example.com"
        # Password hash should have changed
        db_session.refresh(sample_user)
        assert sample_user.password_hash != old_hash
        assert verify_password("BrandNewPass789", sample_user.password_hash)

    def test_update_user_partial_password_fails(self, db_session: Session, sample_user: User, user_use_cases: UserUseCases):
        """Test that providing only current_password without new_password fails"""
        update_data = UserUpdateRequest(
            name="New Name",
            current_password="password123"
            # Missing new_password
        )

        with pytest.raises(ValueError, match="Both current_password and new_password are required"):
            user_use_cases.update_user(
                user_id=sample_user.id,
                data=update_data
            )

    def test_update_user_partial_password_reverse_fails(self, db_session: Session, sample_user: User, user_use_cases: UserUseCases):
        """Test that providing only new_password without current_password fails"""
        update_data = UserUpdateRequest(
            name="New Name",
            new_password="NewPassword123"
            # Missing current_password
        )

        with pytest.raises(ValueError, match="Both current_password and new_password are required"):
            user_use_cases.update_user(
                user_id=sample_user.id,
                data=update_data
            )

    def test_update_user_email_duplicate(self, db_session: Session, sample_user: User, user_use_cases: UserUseCases):
        """Test updating email to one that already exists fails"""
        # Create another user
        other_user = User(
            email="existing@example.com",
            name="Other User",
            password_hash="hashed"
        )
        db_session.add(other_user)
        db_session.commit()

        # Try to update to existing email
        update_data = UserUpdateRequest(
            email="existing@example.com"
        )

        with pytest.raises(ValueError, match="Email already registered"):
            user_use_cases.update_user(
                user_id=sample_user.id,
                data=update_data
            )

    def test_update_user_no_changes(self, db_session: Session, sample_user: User, user_use_cases: UserUseCases):
        """Test update with no changes (all None)"""
        update_data = UserUpdateRequest()

        updated = user_use_cases.update_user(
            user_id=sample_user.id,
            data=update_data
        )

        # Nothing changed
        assert updated.name == "Test User Update"
        assert updated.email == "testuserupdate@example.com"

    def test_update_user_schema_validation(self, db_session: Session):
        """Test that UserUpdateRequest validates correctly"""
        # Valid update with name
        valid = UserUpdateRequest(name="Valid Name")
        assert valid.name == "Valid Name"

        # Valid update with email
        valid_email = UserUpdateRequest(email="valid@example.com")
        assert valid_email.email == "valid@example.com"

        # All None (valid for update - no changes)
        all_none = UserUpdateRequest()
        assert all_none.name is None
        assert all_none.email is None
        assert all_none.current_password is None
        assert all_none.new_password is None

    def test_update_user_repository_level(self, db_session: Session, sample_user: User):
        """Test update at repository level"""
        repo = UserRepository(db_session)

        updated = repo.update(
            user_id=sample_user.id,
            name="Updated via Repo",
            email="repoupdate@example.com"
        )

        assert updated.name == "Updated via Repo"
        assert updated.email == "repoupdate@example.com"

    def test_update_nonexistent_user(self, db_session: Session, user_use_cases: UserUseCases):
        """Test updating non-existent user raises error"""
        from uuid import uuid4
        fake_id = uuid4()

        update_data = UserUpdateRequest(name="Should Fail")

        with pytest.raises(ValueError, match="User not found"):
            user_use_cases.update_user(
                user_id=fake_id,
                data=update_data
            )


class TestPasswordChange:
    """Test suite for dedicated password change operations"""

    def test_change_password_success(self, db_session: Session, sample_user: User, user_use_cases: UserUseCases):
        """Test successful password change"""
        password_data = PasswordChangeRequest(
            current_password="password123",
            new_password="NewSecurePass789"
        )

        result = user_use_cases.change_password(
            user_id=sample_user.id,
            data=password_data
        )

        assert result is True
        # Verify password hash changed
        db_session.refresh(sample_user)
        assert sample_user.password_hash != "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr.TjKwMW"

    def test_change_password_wrong_current(self, db_session: Session, sample_user: User, user_use_cases: UserUseCases):
        """Test password change with wrong current password"""
        password_data = PasswordChangeRequest(
            current_password="wrongpassword",
            new_password="NewPassword123"
        )

        with pytest.raises(ValueError, match="Current password is incorrect"):
            user_use_cases.change_password(
                user_id=sample_user.id,
                data=password_data
            )

    def test_change_password_validation_too_short(self, db_session: Session):
        """Test password validation in PasswordChangeRequest"""
        with pytest.raises(ValueError):
            PasswordChangeRequest(
                current_password="oldpass",
                new_password="short"  # Less than 8 characters
            )

    def test_change_password_same_as_current(self, db_session: Session, sample_user: User, user_use_cases: UserUseCases):
        """Test changing password to same value (should work but is discouraged)"""
        password_data = PasswordChangeRequest(
            current_password="password123",
            new_password="password123"
        )

        # This should technically work (no validation preventing it)
        result = user_use_cases.change_password(
            user_id=sample_user.id,
            data=password_data
        )

        assert result is True
