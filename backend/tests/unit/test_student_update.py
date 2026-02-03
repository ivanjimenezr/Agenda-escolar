"""
Unit tests for Student Update functionality

These tests ensure student profile updates work correctly
with all field types including lists.
"""

import pytest
from uuid import uuid4
from sqlalchemy.orm import Session

from src.domain.models import StudentProfile, User
from src.infrastructure.repositories.student_repository import StudentRepository
from src.application.use_cases.student_use_cases import StudentUseCases
from src.application.schemas.student import StudentUpdateRequest


@pytest.fixture
def sample_user(db_session: Session):
    """Create a sample user for testing"""
    user = User(
        email="teststudentupdate@example.com",
        name="Test Student Update User",
        password_hash="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def student_use_cases(db_session: Session):
    """Create StudentUseCases instance"""
    student_repo = StudentRepository(db_session)
    return StudentUseCases(student_repo)


class TestStudentUpdate:
    """Test suite for student update operations"""

    def test_update_student_basic_fields(self, db_session: Session, sample_user: User, student_use_cases: StudentUseCases):
        """Test updating basic student fields"""
        repo = StudentRepository(db_session)

        student = StudentProfile(
            user_id=sample_user.id,
            name="Original Name",
            school="Original School",
            grade="5th Grade",
            allergies=["gluten"],
            excluded_foods=["nuts"]
        )
        db_session.add(student)
        db_session.commit()
        db_session.refresh(student)

        # Update basic fields
        update_data = StudentUpdateRequest(
            name="Updated Name",
            school="Updated School",
            grade="6th Grade"
        )

        updated = student_use_cases.update_student(
            student_id=student.id,
            user_id=sample_user.id,
            data=update_data
        )

        assert updated.name == "Updated Name"
        assert updated.school == "Updated School"
        assert updated.grade == "6th Grade"
        # Unchanged fields
        assert updated.allergies == ["gluten"]
        assert updated.excluded_foods == ["nuts"]

    def test_update_student_allergies(self, db_session: Session, sample_user: User, student_use_cases: StudentUseCases):
        """Test updating student allergies list"""
        repo = StudentRepository(db_session)

        student = StudentProfile(
            user_id=sample_user.id,
            name="Test Student",
            school="Test School",
            grade="5th",
            allergies=["gluten"],
            excluded_foods=[]
        )
        db_session.add(student)
        db_session.commit()
        db_session.refresh(student)

        # Update allergies
        update_data = StudentUpdateRequest(
            allergies=["gluten", "lactose", "peanuts"]
        )

        updated = student_use_cases.update_student(
            student_id=student.id,
            user_id=sample_user.id,
            data=update_data
        )

        assert len(updated.allergies) == 3
        assert "gluten" in updated.allergies
        assert "lactose" in updated.allergies
        assert "peanuts" in updated.allergies

    def test_update_student_excluded_foods(self, db_session: Session, sample_user: User, student_use_cases: StudentUseCases):
        """Test updating excluded foods list"""
        repo = StudentRepository(db_session)

        student = StudentProfile(
            user_id=sample_user.id,
            name="Test Student",
            school="Test School",
            grade="5th",
            allergies=[],
            excluded_foods=["spinach"]
        )
        db_session.add(student)
        db_session.commit()
        db_session.refresh(student)

        # Update excluded foods
        update_data = StudentUpdateRequest(
            excluded_foods=["spinach", "broccoli", "mushrooms"]
        )

        updated = student_use_cases.update_student(
            student_id=student.id,
            user_id=sample_user.id,
            data=update_data
        )

        assert len(updated.excluded_foods) == 3
        assert "spinach" in updated.excluded_foods
        assert "broccoli" in updated.excluded_foods
        assert "mushrooms" in updated.excluded_foods

    def test_update_student_clear_allergies(self, db_session: Session, sample_user: User, student_use_cases: StudentUseCases):
        """Test clearing allergies list"""
        repo = StudentRepository(db_session)

        student = StudentProfile(
            user_id=sample_user.id,
            name="Test Student",
            school="Test School",
            grade="5th",
            allergies=["gluten", "lactose"],
            excluded_foods=[]
        )
        db_session.add(student)
        db_session.commit()
        db_session.refresh(student)

        # Clear allergies
        update_data = StudentUpdateRequest(
            allergies=[]
        )

        updated = student_use_cases.update_student(
            student_id=student.id,
            user_id=sample_user.id,
            data=update_data
        )

        assert updated.allergies == []

    def test_update_student_avatar_url(self, db_session: Session, sample_user: User, student_use_cases: StudentUseCases):
        """Test updating avatar URL"""
        repo = StudentRepository(db_session)

        student = StudentProfile(
            user_id=sample_user.id,
            name="Test Student",
            school="Test School",
            grade="5th",
            avatar_url=None,
            allergies=[],
            excluded_foods=[]
        )
        db_session.add(student)
        db_session.commit()
        db_session.refresh(student)

        # Add avatar
        update_data = StudentUpdateRequest(
            avatar_url="https://example.com/avatar.jpg"
        )

        updated = student_use_cases.update_student(
            student_id=student.id,
            user_id=sample_user.id,
            data=update_data
        )

        assert updated.avatar_url == "https://example.com/avatar.jpg"

    def test_update_student_remove_avatar(self, db_session: Session, sample_user: User, student_use_cases: StudentUseCases):
        """Test removing avatar URL"""
        repo = StudentRepository(db_session)

        student = StudentProfile(
            user_id=sample_user.id,
            name="Test Student",
            school="Test School",
            grade="5th",
            avatar_url="https://example.com/old.jpg",
            allergies=[],
            excluded_foods=[]
        )
        db_session.add(student)
        db_session.commit()
        db_session.refresh(student)

        # Remove avatar
        update_data = StudentUpdateRequest(
            avatar_url=None
        )

        updated = student_use_cases.update_student(
            student_id=student.id,
            user_id=sample_user.id,
            data=update_data
        )

        assert updated.avatar_url is None

    def test_update_student_all_fields(self, db_session: Session, sample_user: User, student_use_cases: StudentUseCases):
        """Test updating all fields at once"""
        repo = StudentRepository(db_session)

        student = StudentProfile(
            user_id=sample_user.id,
            name="Old Name",
            school="Old School",
            grade="5th",
            avatar_url=None,
            allergies=["old"],
            excluded_foods=["old"]
        )
        db_session.add(student)
        db_session.commit()
        db_session.refresh(student)

        # Update everything
        update_data = StudentUpdateRequest(
            name="New Name",
            school="New School",
            grade="6th",
            avatar_url="https://example.com/new.jpg",
            allergies=["new1", "new2"],
            excluded_foods=["new3", "new4"]
        )

        updated = student_use_cases.update_student(
            student_id=student.id,
            user_id=sample_user.id,
            data=update_data
        )

        assert updated.name == "New Name"
        assert updated.school == "New School"
        assert updated.grade == "6th"
        assert updated.avatar_url == "https://example.com/new.jpg"
        assert updated.allergies == ["new1", "new2"]
        assert updated.excluded_foods == ["new3", "new4"]

    def test_update_student_partial(self, db_session: Session, sample_user: User, student_use_cases: StudentUseCases):
        """Test partial update - only some fields"""
        repo = StudentRepository(db_session)

        student = StudentProfile(
            user_id=sample_user.id,
            name="Original",
            school="Original School",
            grade="5th",
            avatar_url="https://example.com/avatar.jpg",
            allergies=["gluten"],
            excluded_foods=["nuts"]
        )
        db_session.add(student)
        db_session.commit()
        db_session.refresh(student)

        # Update only name
        update_data = StudentUpdateRequest(
            name="Updated Name Only"
        )

        updated = student_use_cases.update_student(
            student_id=student.id,
            user_id=sample_user.id,
            data=update_data
        )

        # Only name changed
        assert updated.name == "Updated Name Only"
        # Others unchanged
        assert updated.school == "Original School"
        assert updated.grade == "5th"
        assert updated.avatar_url == "https://example.com/avatar.jpg"
        assert updated.allergies == ["gluten"]
        assert updated.excluded_foods == ["nuts"]

    def test_update_student_empty_lists(self, db_session: Session, sample_user: User, student_use_cases: StudentUseCases):
        """Test updating with empty lists vs None"""
        repo = StudentRepository(db_session)

        student = StudentProfile(
            user_id=sample_user.id,
            name="Test",
            school="School",
            grade="5th",
            allergies=["item1"],
            excluded_foods=["item2"]
        )
        db_session.add(student)
        db_session.commit()
        db_session.refresh(student)

        # Update with empty lists
        update_data = StudentUpdateRequest(
            allergies=[],
            excluded_foods=[]
        )

        updated = student_use_cases.update_student(
            student_id=student.id,
            user_id=sample_user.id,
            data=update_data
        )

        assert updated.allergies == []
        assert updated.excluded_foods == []

    def test_update_student_schema_validation(self, db_session: Session):
        """Test that StudentUpdateRequest validates correctly"""
        # Valid update
        valid = StudentUpdateRequest(
            name="Valid Name",
            school="Valid School",
            grade="5th Grade"
        )
        assert valid.name == "Valid Name"

        # All None (valid for update - no changes)
        all_none = StudentUpdateRequest()
        assert all_none.name is None
        assert all_none.school is None
        assert all_none.allergies is None

        # Lists
        with_lists = StudentUpdateRequest(
            allergies=["gluten", "lactose"],
            excluded_foods=["nuts", "shellfish"]
        )
        assert len(with_lists.allergies) == 2
        assert len(with_lists.excluded_foods) == 2

    def test_update_student_repository_level(self, db_session: Session, sample_user: User):
        """Test update at repository level"""
        repo = StudentRepository(db_session)

        student = StudentProfile(
            user_id=sample_user.id,
            name="Original",
            school="School",
            grade="5th",
            allergies=[],
            excluded_foods=[]
        )
        db_session.add(student)
        db_session.commit()
        db_session.refresh(student)

        # Update via repository
        updated = repo.update(
            student_id=student.id,
            name="Updated via Repo",
            grade="6th"
        )

        assert updated.name == "Updated via Repo"
        assert updated.grade == "6th"
        assert updated.school == "School"  # Unchanged

    def test_update_nonexistent_student(self, db_session: Session, sample_user: User, student_use_cases: StudentUseCases):
        """Test updating non-existent student raises error"""
        fake_id = uuid4()

        update_data = StudentUpdateRequest(
            name="Should Fail"
        )

        with pytest.raises(ValueError, match="Student not found"):
            student_use_cases.update_student(
                student_id=fake_id,
                user_id=sample_user.id,
                data=update_data
            )

    def test_update_student_different_user(self, db_session: Session, student_use_cases: StudentUseCases):
        """Test updating student with wrong user raises permission error"""
        # Create first user and student
        user1 = User(
            email="user1@example.com",
            name="User 1",
            password_hash="hash"
        )
        db_session.add(user1)
        db_session.commit()
        db_session.refresh(user1)

        student = StudentProfile(
            user_id=user1.id,
            name="Student",
            school="School",
            grade="5th",
            allergies=[],
            excluded_foods=[]
        )
        db_session.add(student)
        db_session.commit()
        db_session.refresh(student)

        # Create second user
        user2 = User(
            email="user2@example.com",
            name="User 2",
            password_hash="hash"
        )
        db_session.add(user2)
        db_session.commit()
        db_session.refresh(user2)

        # Try to update with wrong user
        update_data = StudentUpdateRequest(name="Hacked")

        with pytest.raises(PermissionError, match="Access denied"):
            student_use_cases.update_student(
                student_id=student.id,
                user_id=user2.id,
                data=update_data
            )
