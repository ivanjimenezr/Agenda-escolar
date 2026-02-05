"""
Unit tests for ExamUseCases
"""

from datetime import date
from unittest.mock import MagicMock, Mock
from uuid import uuid4

import pytest

from src.application.schemas.exam import ExamCreateRequest, ExamUpdateRequest
from src.application.use_cases.exam_use_cases import ExamUseCases
from src.domain.models import Exam


@pytest.fixture
def mock_exam_repo():
    """Create mock ExamRepository"""
    return Mock()


@pytest.fixture
def mock_student_repo():
    """Create mock StudentRepository"""
    return Mock()


@pytest.fixture
def exam_use_cases(mock_exam_repo, mock_student_repo):
    """Create ExamUseCases instance with mocked repositories"""
    return ExamUseCases(mock_exam_repo, mock_student_repo)


class TestExamUseCases:
    """Test suite for ExamUseCases"""

    def test_create_exam_success(self, exam_use_cases, mock_exam_repo, mock_student_repo):
        """Test successful exam creation"""
        user_id = uuid4()
        student_id = uuid4()

        # Setup mocks
        mock_student_repo.verify_ownership.return_value = True
        mock_exam = Exam(
            id=uuid4(),
            student_id=student_id,
            subject="Matemáticas",
            date=date(2026, 3, 15),
            topic="Ecuaciones",
            notes="Estudiar bien",
        )
        mock_exam_repo.create.return_value = mock_exam

        # Create request
        request = ExamCreateRequest(
            student_id=student_id,
            subject="Matemáticas",
            date=date(2026, 3, 15),
            topic="Ecuaciones",
            notes="Estudiar bien",
        )

        # Execute
        result = exam_use_cases.create_exam(user_id, request)

        # Verify
        assert result == mock_exam
        mock_student_repo.verify_ownership.assert_called_once_with(student_id, user_id)
        mock_exam_repo.create.assert_called_once_with(
            student_id=student_id,
            subject="Matemáticas",
            date=date(2026, 3, 15),
            topic="Ecuaciones",
            notes="Estudiar bien",
        )

    def test_create_exam_permission_denied(self, exam_use_cases, mock_student_repo):
        """Test exam creation with permission denied"""
        user_id = uuid4()
        student_id = uuid4()

        # Setup mock - ownership verification fails
        mock_student_repo.verify_ownership.return_value = False

        request = ExamCreateRequest(student_id=student_id, subject="Lengua", date=date(2026, 3, 20), topic="Literatura")

        # Execute and verify exception
        with pytest.raises(PermissionError, match="Access denied"):
            exam_use_cases.create_exam(user_id, request)

        mock_student_repo.verify_ownership.assert_called_once_with(student_id, user_id)

    def test_get_exam_by_id_success(self, exam_use_cases, mock_exam_repo, mock_student_repo):
        """Test successfully retrieving an exam by ID"""
        user_id = uuid4()
        exam_id = uuid4()
        student_id = uuid4()

        # Setup mocks
        mock_exam = Exam(
            id=exam_id, student_id=student_id, subject="Historia", date=date(2026, 4, 1), topic="Revolución", notes=None
        )
        mock_exam_repo.get_by_id.return_value = mock_exam
        mock_student_repo.verify_ownership.return_value = True

        # Execute
        result = exam_use_cases.get_exam_by_id(exam_id, user_id)

        # Verify
        assert result == mock_exam
        mock_exam_repo.get_by_id.assert_called_once_with(exam_id)
        mock_student_repo.verify_ownership.assert_called_once_with(student_id, user_id)

    def test_get_exam_by_id_not_found(self, exam_use_cases, mock_exam_repo):
        """Test retrieving non-existent exam"""
        user_id = uuid4()
        exam_id = uuid4()

        # Setup mock - exam not found
        mock_exam_repo.get_by_id.return_value = None

        # Execute and verify exception
        with pytest.raises(ValueError, match="Exam not found"):
            exam_use_cases.get_exam_by_id(exam_id, user_id)

        mock_exam_repo.get_by_id.assert_called_once_with(exam_id)

    def test_get_exam_by_id_permission_denied(self, exam_use_cases, mock_exam_repo, mock_student_repo):
        """Test retrieving exam with permission denied"""
        user_id = uuid4()
        exam_id = uuid4()
        student_id = uuid4()

        # Setup mocks
        mock_exam = Exam(
            id=exam_id, student_id=student_id, subject="Ciencias", date=date(2026, 4, 5), topic="Biología", notes=None
        )
        mock_exam_repo.get_by_id.return_value = mock_exam
        mock_student_repo.verify_ownership.return_value = False

        # Execute and verify exception
        with pytest.raises(PermissionError, match="Access denied"):
            exam_use_cases.get_exam_by_id(exam_id, user_id)

    def test_get_exams_by_student_success(self, exam_use_cases, mock_exam_repo, mock_student_repo):
        """Test successfully retrieving exams for a student"""
        user_id = uuid4()
        student_id = uuid4()

        # Setup mocks
        mock_student_repo.verify_ownership.return_value = True
        mock_exams = [
            Exam(
                id=uuid4(), student_id=student_id, subject="Math", date=date(2026, 3, 10), topic="Topic 1", notes=None
            ),
            Exam(
                id=uuid4(),
                student_id=student_id,
                subject="Science",
                date=date(2026, 3, 15),
                topic="Topic 2",
                notes=None,
            ),
        ]
        mock_exam_repo.get_by_student_id.return_value = mock_exams

        # Execute
        result = exam_use_cases.get_exams_by_student(student_id, user_id)

        # Verify
        assert result == mock_exams
        mock_student_repo.verify_ownership.assert_called_once_with(student_id, user_id)
        mock_exam_repo.get_by_student_id.assert_called_once_with(student_id=student_id, from_date=None, to_date=None)

    def test_get_exams_by_student_with_date_filters(self, exam_use_cases, mock_exam_repo, mock_student_repo):
        """Test retrieving exams with date filters"""
        user_id = uuid4()
        student_id = uuid4()
        from_date = date(2026, 3, 1)
        to_date = date(2026, 3, 31)

        # Setup mocks
        mock_student_repo.verify_ownership.return_value = True
        mock_exam_repo.get_by_student_id.return_value = []

        # Execute
        exam_use_cases.get_exams_by_student(student_id, user_id, from_date=from_date, to_date=to_date)

        # Verify
        mock_exam_repo.get_by_student_id.assert_called_once_with(
            student_id=student_id, from_date=from_date, to_date=to_date
        )

    def test_get_exams_by_student_permission_denied(self, exam_use_cases, mock_student_repo):
        """Test retrieving exams with permission denied"""
        user_id = uuid4()
        student_id = uuid4()

        # Setup mock - ownership verification fails
        mock_student_repo.verify_ownership.return_value = False

        # Execute and verify exception
        with pytest.raises(PermissionError, match="Access denied"):
            exam_use_cases.get_exams_by_student(student_id, user_id)

        mock_student_repo.verify_ownership.assert_called_once_with(student_id, user_id)

    def test_update_exam_success(self, exam_use_cases, mock_exam_repo, mock_student_repo):
        """Test successfully updating an exam"""
        user_id = uuid4()
        exam_id = uuid4()
        student_id = uuid4()

        # Setup mocks
        mock_exam = Exam(
            id=exam_id, student_id=student_id, subject="Physics", date=date(2026, 4, 10), topic="Mechanics", notes=None
        )
        mock_exam_repo.get_by_id.return_value = mock_exam
        mock_student_repo.verify_ownership.return_value = True

        updated_exam = Exam(
            id=exam_id,
            student_id=student_id,
            subject="Advanced Physics",
            date=date(2026, 4, 15),
            topic="Quantum Mechanics",
            notes="Review chapters 5-7",
        )
        mock_exam_repo.update.return_value = updated_exam

        request = ExamUpdateRequest(
            subject="Advanced Physics", date=date(2026, 4, 15), topic="Quantum Mechanics", notes="Review chapters 5-7"
        )

        # Execute
        result = exam_use_cases.update_exam(exam_id, user_id, request)

        # Verify
        assert result == updated_exam
        mock_exam_repo.get_by_id.assert_called_once_with(exam_id)
        mock_student_repo.verify_ownership.assert_called_once_with(student_id, user_id)
        mock_exam_repo.update.assert_called_once_with(
            exam_id=exam_id,
            subject="Advanced Physics",
            date=date(2026, 4, 15),
            topic="Quantum Mechanics",
            notes="Review chapters 5-7",
        )

    def test_update_exam_not_found(self, exam_use_cases, mock_exam_repo):
        """Test updating non-existent exam"""
        user_id = uuid4()
        exam_id = uuid4()

        # Setup mock - exam not found
        mock_exam_repo.get_by_id.return_value = None

        request = ExamUpdateRequest(subject="New Subject")

        # Execute and verify exception
        with pytest.raises(ValueError, match="Exam not found"):
            exam_use_cases.update_exam(exam_id, user_id, request)

    def test_update_exam_permission_denied(self, exam_use_cases, mock_exam_repo, mock_student_repo):
        """Test updating exam with permission denied"""
        user_id = uuid4()
        exam_id = uuid4()
        student_id = uuid4()

        # Setup mocks
        mock_exam = Exam(
            id=exam_id,
            student_id=student_id,
            subject="Chemistry",
            date=date(2026, 4, 20),
            topic="Reactions",
            notes=None,
        )
        mock_exam_repo.get_by_id.return_value = mock_exam
        mock_student_repo.verify_ownership.return_value = False

        request = ExamUpdateRequest(subject="Organic Chemistry")

        # Execute and verify exception
        with pytest.raises(PermissionError, match="Access denied"):
            exam_use_cases.update_exam(exam_id, user_id, request)

    def test_delete_exam_success(self, exam_use_cases, mock_exam_repo, mock_student_repo):
        """Test successfully deleting an exam"""
        user_id = uuid4()
        exam_id = uuid4()
        student_id = uuid4()

        # Setup mocks
        mock_exam = Exam(
            id=exam_id,
            student_id=student_id,
            subject="Geography",
            date=date(2026, 5, 1),
            topic="Continents",
            notes=None,
        )
        mock_exam_repo.get_by_id.return_value = mock_exam
        mock_student_repo.verify_ownership.return_value = True
        mock_exam_repo.delete.return_value = True

        # Execute
        result = exam_use_cases.delete_exam(exam_id, user_id)

        # Verify
        assert result is True
        mock_exam_repo.get_by_id.assert_called_once_with(exam_id)
        mock_student_repo.verify_ownership.assert_called_once_with(student_id, user_id)
        mock_exam_repo.delete.assert_called_once_with(exam_id)

    def test_delete_exam_not_found(self, exam_use_cases, mock_exam_repo):
        """Test deleting non-existent exam"""
        user_id = uuid4()
        exam_id = uuid4()

        # Setup mock - exam not found
        mock_exam_repo.get_by_id.return_value = None

        # Execute and verify exception
        with pytest.raises(ValueError, match="Exam not found"):
            exam_use_cases.delete_exam(exam_id, user_id)

    def test_delete_exam_permission_denied(self, exam_use_cases, mock_exam_repo, mock_student_repo):
        """Test deleting exam with permission denied"""
        user_id = uuid4()
        exam_id = uuid4()
        student_id = uuid4()

        # Setup mocks
        mock_exam = Exam(
            id=exam_id, student_id=student_id, subject="Art", date=date(2026, 5, 5), topic="Renaissance", notes=None
        )
        mock_exam_repo.get_by_id.return_value = mock_exam
        mock_student_repo.verify_ownership.return_value = False

        # Execute and verify exception
        with pytest.raises(PermissionError, match="Access denied"):
            exam_use_cases.delete_exam(exam_id, user_id)
