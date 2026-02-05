"""
Unit tests for StudentRepository
"""

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from src.domain.models import StudentProfile, User
from src.infrastructure.repositories.student_repository import StudentRepository


@pytest.fixture
def sample_user(db_session: Session):
    """Create a sample user for testing"""
    user = User(email="test@example.com", name="Test User", password_hash="hashed_password")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestStudentRepository:
    """Test suite for StudentRepository"""

    def test_create_student(self, db_session: Session, sample_user: User):
        """Test creating a new student profile"""
        repo = StudentRepository(db_session)

        student = repo.create(
            user_id=sample_user.id,
            name="John Doe",
            school="Test School",
            grade="5th Grade",
            avatar_url="https://example.com/avatar.jpg",
            allergies=["gluten"],
            excluded_foods=["fish"],
        )

        assert student.id is not None
        assert student.user_id == sample_user.id
        assert student.name == "John Doe"
        assert student.school == "Test School"
        assert student.grade == "5th Grade"
        assert student.avatar_url == "https://example.com/avatar.jpg"
        assert student.allergies == ["gluten"]
        assert student.excluded_foods == ["fish"]
        assert student.created_at is not None
        assert student.updated_at is not None

    def test_get_by_id_existing(self, db_session: Session, sample_user: User):
        """Test retrieving an existing student by ID"""
        repo = StudentRepository(db_session)

        student = repo.create(user_id=sample_user.id, name="Jane Smith", school="Test School", grade="3rd Grade")

        retrieved = repo.get_by_id(student.id)

        assert retrieved is not None
        assert retrieved.id == student.id
        assert retrieved.name == "Jane Smith"

    def test_get_by_id_nonexistent(self, db_session: Session):
        """Test retrieving a non-existent student returns None"""
        repo = StudentRepository(db_session)

        result = repo.get_by_id(uuid4())

        assert result is None

    def test_get_by_user_id(self, db_session: Session, sample_user: User):
        """Test retrieving all students for a user"""
        repo = StudentRepository(db_session)

        student1 = repo.create(user_id=sample_user.id, name="Child 1", school="School A", grade="1st Grade")
        student2 = repo.create(user_id=sample_user.id, name="Child 2", school="School B", grade="2nd Grade")

        students = repo.get_by_user_id(sample_user.id)

        assert len(students) == 2
        assert student1 in students
        assert student2 in students

    def test_get_by_user_id_empty(self, db_session: Session, sample_user: User):
        """Test retrieving students when user has none"""
        repo = StudentRepository(db_session)

        students = repo.get_by_user_id(sample_user.id)

        assert students == []

    def test_update_student(self, db_session: Session, sample_user: User):
        """Test updating a student profile"""
        repo = StudentRepository(db_session)

        student = repo.create(user_id=sample_user.id, name="Original Name", school="Original School", grade="1st Grade")

        updated = repo.update(
            student_id=student.id,
            name="Updated Name",
            school="Updated School",
            grade="2nd Grade",
            allergies=["lactose"],
            excluded_foods=["nuts"],
        )

        assert updated.name == "Updated Name"
        assert updated.school == "Updated School"
        assert updated.grade == "2nd Grade"
        assert updated.allergies == ["lactose"]
        assert updated.excluded_foods == ["nuts"]

    def test_update_partial(self, db_session: Session, sample_user: User):
        """Test partial update of student profile"""
        repo = StudentRepository(db_session)

        student = repo.create(
            user_id=sample_user.id, name="John Doe", school="School A", grade="1st Grade", allergies=["gluten"]
        )

        updated = repo.update(student_id=student.id, name="Jane Doe")

        assert updated.name == "Jane Doe"
        assert updated.school == "School A"  # Unchanged
        assert updated.grade == "1st Grade"  # Unchanged
        assert updated.allergies == ["gluten"]  # Unchanged

    def test_delete_student(self, db_session: Session, sample_user: User):
        """Test soft deleting a student"""
        repo = StudentRepository(db_session)

        student = repo.create(user_id=sample_user.id, name="To Delete", school="Test School", grade="1st Grade")

        result = repo.delete(student.id)

        assert result is True

        # Student should not be retrievable
        retrieved = repo.get_by_id(student.id)
        assert retrieved is None

        # But should exist in DB with deleted_at set
        deleted_student = db_session.query(StudentProfile).filter(StudentProfile.id == student.id).first()
        assert deleted_student is not None
        assert deleted_student.deleted_at is not None

    def test_delete_nonexistent(self, db_session: Session):
        """Test deleting a non-existent student returns False"""
        repo = StudentRepository(db_session)

        result = repo.delete(uuid4())

        assert result is False

    def test_verify_ownership_true(self, db_session: Session, sample_user: User):
        """Test verifying student ownership returns True for owner"""
        repo = StudentRepository(db_session)

        student = repo.create(user_id=sample_user.id, name="Test Student", school="Test School", grade="1st Grade")

        result = repo.verify_ownership(student.id, sample_user.id)

        assert result is True

    def test_verify_ownership_false(self, db_session: Session, sample_user: User):
        """Test verifying student ownership returns False for non-owner"""
        repo = StudentRepository(db_session)

        student = repo.create(user_id=sample_user.id, name="Test Student", school="Test School", grade="1st Grade")

        other_user_id = uuid4()
        result = repo.verify_ownership(student.id, other_user_id)

        assert result is False

    def test_verify_ownership_nonexistent(self, db_session: Session, sample_user: User):
        """Test verifying ownership of non-existent student returns False"""
        repo = StudentRepository(db_session)

        result = repo.verify_ownership(uuid4(), sample_user.id)

        assert result is False

    def test_get_by_id_excludes_soft_deleted(self, db_session: Session, sample_user: User):
        """Test that get_by_id doesn't return soft-deleted students"""
        repo = StudentRepository(db_session)

        student = repo.create(user_id=sample_user.id, name="Test Student", school="Test School", grade="1st Grade")

        repo.delete(student.id)

        retrieved = repo.get_by_id(student.id)
        assert retrieved is None

    def test_get_by_user_id_excludes_soft_deleted(self, db_session: Session, sample_user: User):
        """Test that get_by_user_id doesn't return soft-deleted students"""
        repo = StudentRepository(db_session)

        student1 = repo.create(user_id=sample_user.id, name="Active Student", school="Test School", grade="1st Grade")
        student2 = repo.create(user_id=sample_user.id, name="Deleted Student", school="Test School", grade="2nd Grade")

        repo.delete(student2.id)

        students = repo.get_by_user_id(sample_user.id)

        assert len(students) == 1
        assert students[0].id == student1.id
