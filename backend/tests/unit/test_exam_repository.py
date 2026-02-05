"""
Unit tests for ExamRepository
"""

from datetime import date, datetime
from uuid import uuid4

import pytest

from src.domain.models import Exam, StudentProfile, User
from src.infrastructure.repositories.exam_repository import ExamRepository


@pytest.fixture
def exam_repo(db_session):
    """Create ExamRepository instance with test database session."""
    return ExamRepository(db_session)


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(
        id=uuid4(),
        email="exam_test@example.com",
        name="Exam Test User",
        password_hash="dummy_hash",
        is_active=True,
        email_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_student(db_session, sample_user):
    """Create a sample student for testing."""
    student = StudentProfile(
        id=uuid4(),
        user_id=sample_user.id,
        name="Test Student",
        school="Test School",
        grade="5º",
        allergies=[],
        excluded_foods=[],
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


class TestExamRepository:
    """Test suite for ExamRepository"""

    def test_create_exam(self, exam_repo, sample_student):
        """Test creating a new exam"""
        exam = exam_repo.create(
            student_id=sample_student.id,
            subject="Matemáticas",
            date=date(2026, 3, 15),
            topic="Ecuaciones de segundo grado",
            notes="Repasar ejercicios 1-10",
        )

        assert exam.id is not None
        assert exam.student_id == sample_student.id
        assert exam.subject == "Matemáticas"
        assert exam.date == date(2026, 3, 15)
        assert exam.topic == "Ecuaciones de segundo grado"
        assert exam.notes == "Repasar ejercicios 1-10"
        assert exam.created_at is not None
        assert exam.updated_at is not None

    def test_create_exam_without_notes(self, exam_repo, sample_student):
        """Test creating an exam without notes"""
        exam = exam_repo.create(
            student_id=sample_student.id, subject="Lengua", date=date(2026, 3, 20), topic="Análisis sintáctico"
        )

        assert exam.id is not None
        assert exam.notes is None

    def test_get_by_id(self, exam_repo, sample_student):
        """Test retrieving an exam by ID"""
        created = exam_repo.create(
            student_id=sample_student.id, subject="Historia", date=date(2026, 4, 1), topic="Revolución francesa"
        )

        retrieved = exam_repo.get_by_id(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.subject == "Historia"
        assert retrieved.topic == "Revolución francesa"

    def test_get_by_id_not_found(self, exam_repo):
        """Test retrieving a non-existent exam"""
        result = exam_repo.get_by_id(uuid4())
        assert result is None

    def test_get_by_student_id(self, exam_repo, sample_student):
        """Test retrieving all exams for a student"""
        # Create multiple exams
        exam1 = exam_repo.create(
            student_id=sample_student.id, subject="Matemáticas", date=date(2026, 3, 15), topic="Tema 1"
        )
        exam2 = exam_repo.create(student_id=sample_student.id, subject="Lengua", date=date(2026, 3, 10), topic="Tema 2")
        exam3 = exam_repo.create(
            student_id=sample_student.id, subject="Historia", date=date(2026, 3, 20), topic="Tema 3"
        )

        exams = exam_repo.get_by_student_id(sample_student.id)

        assert len(exams) == 3
        # Should be ordered by date ascending
        assert exams[0].date == date(2026, 3, 10)
        assert exams[1].date == date(2026, 3, 15)
        assert exams[2].date == date(2026, 3, 20)

    def test_get_by_student_id_with_date_filters(self, exam_repo, sample_student):
        """Test retrieving exams with date range filters"""
        # Create exams on different dates
        exam_repo.create(student_id=sample_student.id, subject="Math", date=date(2026, 3, 1), topic="Topic 1")
        exam_repo.create(student_id=sample_student.id, subject="Science", date=date(2026, 3, 15), topic="Topic 2")
        exam_repo.create(student_id=sample_student.id, subject="History", date=date(2026, 3, 30), topic="Topic 3")

        # Test from_date filter
        exams = exam_repo.get_by_student_id(sample_student.id, from_date=date(2026, 3, 10))
        assert len(exams) == 2
        assert all(e.date >= date(2026, 3, 10) for e in exams)

        # Test to_date filter
        exams = exam_repo.get_by_student_id(sample_student.id, to_date=date(2026, 3, 20))
        assert len(exams) == 2
        assert all(e.date <= date(2026, 3, 20) for e in exams)

        # Test both filters
        exams = exam_repo.get_by_student_id(sample_student.id, from_date=date(2026, 3, 10), to_date=date(2026, 3, 20))
        assert len(exams) == 1
        assert exams[0].date == date(2026, 3, 15)

    def test_update_exam(self, exam_repo, sample_student):
        """Test updating an exam"""
        exam = exam_repo.create(
            student_id=sample_student.id, subject="Biology", date=date(2026, 4, 1), topic="Cell structure"
        )

        original_updated_at = exam.updated_at

        # Update the exam
        updated = exam_repo.update(
            exam_id=exam.id,
            subject="Advanced Biology",
            date=date(2026, 4, 5),
            topic="Cell structure and mitosis",
            notes="Study chapters 3-5",
        )

        assert updated is not None
        assert updated.subject == "Advanced Biology"
        assert updated.date == date(2026, 4, 5)
        assert updated.topic == "Cell structure and mitosis"
        assert updated.notes == "Study chapters 3-5"
        assert updated.updated_at > original_updated_at

    def test_update_partial(self, exam_repo, sample_student):
        """Test partial update of an exam"""
        exam = exam_repo.create(
            student_id=sample_student.id, subject="Chemistry", date=date(2026, 4, 10), topic="Periodic table"
        )

        # Only update the topic
        updated = exam_repo.update(exam_id=exam.id, topic="Periodic table and chemical bonds")

        assert updated is not None
        assert updated.subject == "Chemistry"  # Unchanged
        assert updated.date == date(2026, 4, 10)  # Unchanged
        assert updated.topic == "Periodic table and chemical bonds"  # Changed

    def test_update_not_found(self, exam_repo):
        """Test updating a non-existent exam"""
        result = exam_repo.update(exam_id=uuid4(), subject="New Subject")
        assert result is None

    def test_hard_delete(self, exam_repo, sample_student):
        """Test hard delete (permanent deletion)"""
        exam = exam_repo.create(
            student_id=sample_student.id, subject="Physics", date=date(2026, 5, 1), topic="Mechanics"
        )

        exam_id = exam.id

        # Delete the exam
        result = exam_repo.delete(exam_id)
        assert result is True

        # Verify it's permanently deleted
        deleted_exam = exam_repo.get_by_id(exam_id)
        assert deleted_exam is None

    def test_delete_not_found(self, exam_repo):
        """Test deleting a non-existent exam"""
        result = exam_repo.delete(uuid4())
        assert result is False

    def test_exams_isolated_by_student(self, exam_repo, db_session, sample_user):
        """Test that exams are properly isolated by student"""
        # Create two students
        student1 = StudentProfile(
            id=uuid4(),
            user_id=sample_user.id,
            name="Student 1",
            school="School 1",
            grade="4º",
            allergies=[],
            excluded_foods=[],
        )
        student2 = StudentProfile(
            id=uuid4(),
            user_id=sample_user.id,
            name="Student 2",
            school="School 2",
            grade="6º",
            allergies=[],
            excluded_foods=[],
        )
        db_session.add_all([student1, student2])
        db_session.commit()

        # Create exams for each student
        exam_repo.create(student_id=student1.id, subject="Math", date=date(2026, 3, 15), topic="Topic 1")
        exam_repo.create(student_id=student2.id, subject="Science", date=date(2026, 3, 15), topic="Topic 2")

        # Verify isolation
        student1_exams = exam_repo.get_by_student_id(student1.id)
        student2_exams = exam_repo.get_by_student_id(student2.id)

        assert len(student1_exams) == 1
        assert len(student2_exams) == 1
        assert student1_exams[0].subject == "Math"
        assert student2_exams[0].subject == "Science"
