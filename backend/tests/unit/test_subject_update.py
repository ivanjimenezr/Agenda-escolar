"""
Unit tests for Subject Update functionality

These tests specifically focus on the update operation with various
field combinations, especially the time field which was causing issues.
"""

import pytest
from datetime import time
from uuid import uuid4
from sqlalchemy.orm import Session

from src.domain.models import StudentProfile, User, Subject
from src.infrastructure.repositories.subject_repository import SubjectRepository
from src.application.use_cases.subject_use_cases import SubjectUseCases
from src.application.schemas.subject import SubjectUpdateRequest
from src.infrastructure.repositories.student_repository import StudentRepository


@pytest.fixture
def sample_user(db_session: Session):
    """Create a sample user for testing"""
    user = User(
        email="testupdate@example.com",
        name="Test Update User",
        password_hash="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_student(db_session: Session, sample_user: User):
    """Create a sample student for testing"""
    student = StudentProfile(
        user_id=sample_user.id,
        name="Test Student Update",
        school="Test School",
        grade="5th Grade"
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


@pytest.fixture
def subject_use_cases(db_session: Session):
    """Create SubjectUseCases instance"""
    subject_repo = SubjectRepository(db_session)
    student_repo = StudentRepository(db_session)
    return SubjectUseCases(subject_repo, student_repo)


class TestSubjectUpdate:
    """Test suite for subject update operations"""

    def test_update_subject_with_time_filled(self, db_session: Session, sample_student: StudentProfile, sample_user: User, subject_use_cases: SubjectUseCases):
        """Test updating a subject when time field is filled - this was the failing case"""
        # Create initial subject
        repo = SubjectRepository(db_session)
        subject = repo.create(
            student_id=sample_student.id,
            name="Matemáticas",
            days=["Lunes", "Miércoles"],
            time=time(9, 0),
            teacher="Prof. García",
            color="#FF5733",
            type="colegio"
        )

        # Update with time field filled
        update_data = SubjectUpdateRequest(
            name="Matemáticas Avanzadas",
            time=time(10, 30),  # Changed time
            teacher="Prof. López"
        )

        updated = subject_use_cases.update_subject(
            subject_id=subject.id,
            user_id=sample_user.id,
            data=update_data
        )

        assert updated.name == "Matemáticas Avanzadas"
        assert updated.time == time(10, 30)
        assert updated.teacher == "Prof. López"
        # Unchanged fields
        assert updated.days == ["Lunes", "Miércoles"]
        assert updated.color == "#FF5733"

    def test_update_subject_time_from_string(self, db_session: Session, sample_student: StudentProfile):
        """Test updating subject with time as string (as received from frontend)"""
        repo = SubjectRepository(db_session)

        subject = repo.create(
            student_id=sample_student.id,
            name="Lengua",
            days=["Martes"],
            time=time(9, 0),
            teacher="Prof. A",
            color="#00FF00",
            type="colegio"
        )

        # Simulate frontend sending time as string
        from pydantic import ValidationError

        try:
            update_data = SubjectUpdateRequest(
                time="11:30:00"  # String format
            )

            # The validator should parse this
            assert update_data.time == time(11, 30, 0)

            # Update via repository
            updated = repo.update(
                subject_id=subject.id,
                time=update_data.time
            )

            assert updated.time == time(11, 30, 0)
        except ValidationError as e:
            pytest.fail(f"Failed to parse time string: {e}")

    def test_update_subject_time_only(self, db_session: Session, sample_student: StudentProfile, sample_user: User, subject_use_cases: SubjectUseCases):
        """Test updating ONLY the time field"""
        repo = SubjectRepository(db_session)

        subject = repo.create(
            student_id=sample_student.id,
            name="Inglés",
            days=["Jueves", "Viernes"],
            time=time(12, 0),
            teacher="Prof. Smith",
            color="#0000FF",
            type="extraescolar"
        )

        # Update ONLY time
        update_data = SubjectUpdateRequest(
            time=time(14, 0)
        )

        updated = subject_use_cases.update_subject(
            subject_id=subject.id,
            user_id=sample_user.id,
            data=update_data
        )

        # Only time should change
        assert updated.time == time(14, 0)
        # Everything else unchanged
        assert updated.name == "Inglés"
        assert updated.days == ["Jueves", "Viernes"]
        assert updated.teacher == "Prof. Smith"
        assert updated.color == "#0000FF"
        assert updated.type == "extraescolar"

    def test_update_subject_without_time(self, db_session: Session, sample_student: StudentProfile, sample_user: User, subject_use_cases: SubjectUseCases):
        """Test updating subject without touching time field"""
        repo = SubjectRepository(db_session)

        subject = repo.create(
            student_id=sample_student.id,
            name="Ciencias",
            days=["Lunes"],
            time=time(15, 30),
            teacher="Prof. Pérez",
            color="#FFAA00",
            type="colegio"
        )

        original_time = subject.time

        # Update without time field
        update_data = SubjectUpdateRequest(
            name="Ciencias Naturales",
            teacher="Prof. González"
        )

        updated = subject_use_cases.update_subject(
            subject_id=subject.id,
            user_id=sample_user.id,
            data=update_data
        )

        # Time should remain unchanged
        assert updated.time == original_time
        assert updated.time == time(15, 30)
        # Other fields updated
        assert updated.name == "Ciencias Naturales"
        assert updated.teacher == "Prof. González"

    def test_update_subject_with_time_none(self, db_session: Session, sample_student: StudentProfile):
        """Test updating subject with time=None explicitly"""
        repo = SubjectRepository(db_session)

        subject = repo.create(
            student_id=sample_student.id,
            name="Arte",
            days=["Miércoles"],
            time=time(16, 0),
            teacher="Prof. Artista",
            color="#FF00FF",
            type="extraescolar"
        )

        # Update with time=None (should not change)
        update_data = SubjectUpdateRequest(
            name="Arte Moderno",
            time=None  # Explicitly None
        )

        # Time is Optional, so None means "don't update"
        updated = repo.update(
            subject_id=subject.id,
            name=update_data.name,
            time=update_data.time
        )

        # time=None should mean "don't change it"
        assert updated.time == time(16, 0)  # Unchanged
        assert updated.name == "Arte Moderno"

    def test_update_subject_all_fields_including_time(self, db_session: Session, sample_student: StudentProfile, sample_user: User, subject_use_cases: SubjectUseCases):
        """Test updating ALL fields including time"""
        repo = SubjectRepository(db_session)

        subject = repo.create(
            student_id=sample_student.id,
            name="Old Name",
            days=["Lunes"],
            time=time(9, 0),
            teacher="Old Teacher",
            color="#000000",
            type="colegio"
        )

        # Update everything
        update_data = SubjectUpdateRequest(
            name="New Name",
            days=["Martes", "Jueves"],
            time=time(11, 30),
            teacher="New Teacher",
            color="#FFFFFF",
            type="extraescolar"
        )

        updated = subject_use_cases.update_subject(
            subject_id=subject.id,
            user_id=sample_user.id,
            data=update_data
        )

        assert updated.name == "New Name"
        assert updated.days == ["Martes", "Jueves"]
        assert updated.time == time(11, 30)
        assert updated.teacher == "New Teacher"
        assert updated.color == "#FFFFFF"
        assert updated.type == "extraescolar"

    def test_update_subject_time_with_various_formats(self, db_session: Session, sample_student: StudentProfile):
        """Test time field accepts various string formats"""
        repo = SubjectRepository(db_session)

        subject = repo.create(
            student_id=sample_student.id,
            name="Test",
            days=["Lunes"],
            time=time(9, 0),
            teacher="Test",
            color="#123456",
            type="colegio"
        )

        # Test HH:MM format
        update_data1 = SubjectUpdateRequest(time="14:30")
        assert update_data1.time == time(14, 30, 0)

        # Test HH:MM:SS format
        update_data2 = SubjectUpdateRequest(time="14:30:45")
        assert update_data2.time == time(14, 30, 45)

        # Test with leading zeros
        update_data3 = SubjectUpdateRequest(time="09:05:03")
        assert update_data3.time == time(9, 5, 3)

    def test_update_subject_repository_level(self, db_session: Session, sample_student: StudentProfile):
        """Test update at repository level with time"""
        repo = SubjectRepository(db_session)

        subject = repo.create(
            student_id=sample_student.id,
            name="Repo Test",
            days=["Viernes"],
            time=time(10, 0),
            teacher="Test Teacher",
            color="#AABBCC",
            type="colegio"
        )

        # Update via repository
        updated = repo.update(
            subject_id=subject.id,
            time=time(13, 45),
            name="Updated Repo Test"
        )

        assert updated.time == time(13, 45)
        assert updated.name == "Updated Repo Test"
        # Others unchanged
        assert updated.days == ["Viernes"]
        assert updated.teacher == "Test Teacher"

    def test_update_subject_time_edge_cases(self, db_session: Session, sample_student: StudentProfile):
        """Test edge cases for time values"""
        repo = SubjectRepository(db_session)

        subject = repo.create(
            student_id=sample_student.id,
            name="Edge Case Test",
            days=["Lunes"],
            time=time(12, 0),
            teacher="Test",
            color="#111111",
            type="colegio"
        )

        # Midnight
        update_data1 = SubjectUpdateRequest(time="00:00:00")
        assert update_data1.time == time(0, 0, 0)

        # Almost midnight
        update_data2 = SubjectUpdateRequest(time="23:59:59")
        assert update_data2.time == time(23, 59, 59)

        # Noon
        update_data3 = SubjectUpdateRequest(time="12:00:00")
        assert update_data3.time == time(12, 0, 0)

    def test_update_subject_with_empty_teacher(self, db_session: Session, sample_student: StudentProfile, sample_user: User, subject_use_cases: SubjectUseCases):
        """Test updating subject with empty teacher string"""
        repo = SubjectRepository(db_session)

        subject = repo.create(
            student_id=sample_student.id,
            name="No Teacher Subject",
            days=["Lunes"],
            time=time(9, 0),
            teacher="Original Teacher",
            color="#FF0000",
            type="colegio"
        )

        # Update with empty teacher (validator should convert to None)
        update_data = SubjectUpdateRequest(
            teacher=""  # Empty string
        )

        # The validator should convert empty string to None
        assert update_data.teacher is None

        updated = subject_use_cases.update_subject(
            subject_id=subject.id,
            user_id=sample_user.id,
            data=update_data
        )

        # Teacher should be None or empty string depending on implementation
        assert updated.teacher is None or updated.teacher == ""

    def test_update_multiple_subjects_with_same_time(self, db_session: Session, sample_student: StudentProfile, sample_user: User, subject_use_cases: SubjectUseCases):
        """Test updating multiple subjects to have the same time (different days)"""
        repo = SubjectRepository(db_session)

        subject1 = repo.create(
            student_id=sample_student.id,
            name="Subject 1",
            days=["Lunes"],
            time=time(9, 0),
            teacher="Teacher 1",
            color="#FF0000",
            type="colegio"
        )

        subject2 = repo.create(
            student_id=sample_student.id,
            name="Subject 2",
            days=["Martes"],
            time=time(10, 0),
            teacher="Teacher 2",
            color="#00FF00",
            type="colegio"
        )

        # Update both to same time (different days, so no conflict)
        new_time = time(11, 30)

        updated1 = subject_use_cases.update_subject(
            subject_id=subject1.id,
            user_id=sample_user.id,
            data=SubjectUpdateRequest(time=new_time)
        )

        updated2 = subject_use_cases.update_subject(
            subject_id=subject2.id,
            user_id=sample_user.id,
            data=SubjectUpdateRequest(time=new_time)
        )

        assert updated1.time == new_time
        assert updated2.time == new_time
        # Days are different, so no conflict
        assert updated1.days == ["Lunes"]
        assert updated2.days == ["Martes"]
