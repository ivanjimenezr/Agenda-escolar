"""
Unit tests for StudentUseCases
"""

from unittest.mock import Mock
from uuid import uuid4

import pytest

from src.application.schemas.student import StudentCreateRequest, StudentUpdateRequest
from src.application.use_cases.student_use_cases import StudentUseCases
from src.domain.models import StudentProfile


@pytest.fixture
def mock_repository():
    """Create a mock StudentRepository"""
    return Mock()


@pytest.fixture
def use_cases(mock_repository):
    """Create StudentUseCases with mock repository"""
    return StudentUseCases(mock_repository)


class TestStudentUseCases:
    """Test suite for StudentUseCases"""

    def test_create_student_success(self, use_cases, mock_repository):
        """Test successful student creation"""
        user_id = uuid4()
        request = StudentCreateRequest(
            name="John Doe",
            school="Test School",
            grade="5th Grade",
            avatar_url="https://example.com/avatar.jpg",
            allergies=["gluten"],
            excluded_foods=["fish"],
        )

        mock_student = StudentProfile(
            id=uuid4(),
            user_id=user_id,
            name="John Doe",
            school="Test School",
            grade="5th Grade",
            avatar_url="https://example.com/avatar.jpg",
            allergies=["gluten"],
            excluded_foods=["fish"],
        )
        mock_repository.create.return_value = mock_student

        result = use_cases.create_student(user_id, request)

        assert result == mock_student
        mock_repository.create.assert_called_once_with(
            user_id=user_id,
            name="John Doe",
            school="Test School",
            grade="5th Grade",
            avatar_url="https://example.com/avatar.jpg",
            allergies=["gluten"],
            excluded_foods=["fish"],
        )

    def test_get_student_by_id_success(self, use_cases, mock_repository):
        """Test successful retrieval of student by ID"""
        student_id = uuid4()
        user_id = uuid4()
        mock_student = StudentProfile(
            id=student_id, user_id=user_id, name="Test Student", school="Test School", grade="1st Grade"
        )

        mock_repository.get_by_id.return_value = mock_student
        mock_repository.verify_ownership.return_value = True

        result = use_cases.get_student_by_id(student_id, user_id)

        assert result == mock_student
        mock_repository.get_by_id.assert_called_once_with(student_id)
        mock_repository.verify_ownership.assert_called_once_with(student_id, user_id)

    def test_get_student_by_id_not_found(self, use_cases, mock_repository):
        """Test retrieving non-existent student raises ValueError"""
        student_id = uuid4()
        user_id = uuid4()

        mock_repository.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Student not found"):
            use_cases.get_student_by_id(student_id, user_id)

    def test_get_student_by_id_unauthorized(self, use_cases, mock_repository):
        """Test accessing another user's student raises PermissionError"""
        student_id = uuid4()
        user_id = uuid4()
        mock_student = StudentProfile(
            id=student_id,
            user_id=uuid4(),  # Different user
            name="Test Student",
            school="Test School",
            grade="1st Grade",
        )

        mock_repository.get_by_id.return_value = mock_student
        mock_repository.verify_ownership.return_value = False

        with pytest.raises(PermissionError, match="Access denied"):
            use_cases.get_student_by_id(student_id, user_id)

    def test_get_students_by_user(self, use_cases, mock_repository):
        """Test retrieving all students for a user"""
        user_id = uuid4()
        mock_students = [
            StudentProfile(id=uuid4(), user_id=user_id, name="Student 1", school="School A", grade="1st Grade"),
            StudentProfile(id=uuid4(), user_id=user_id, name="Student 2", school="School B", grade="2nd Grade"),
        ]

        mock_repository.get_by_user_id.return_value = mock_students

        result = use_cases.get_students_by_user(user_id)

        assert result == mock_students
        mock_repository.get_by_user_id.assert_called_once_with(user_id)

    def test_update_student_success(self, use_cases, mock_repository):
        """Test successful student update"""
        student_id = uuid4()
        user_id = uuid4()
        request = StudentUpdateRequest(name="Updated Name", school="Updated School")

        mock_student = StudentProfile(
            id=student_id, user_id=user_id, name="Updated Name", school="Updated School", grade="5th Grade"
        )

        mock_repository.get_by_id.return_value = mock_student
        mock_repository.update.return_value = mock_student

        result = use_cases.update_student(student_id, user_id, request)

        assert result == mock_student
        mock_repository.get_by_id.assert_called_once_with(student_id)
        mock_repository.update.assert_called_once_with(
            student_id=student_id,
            name="Updated Name",
            school="Updated School",
            grade=None,
            avatar_url=None,
            allergies=None,
            excluded_foods=None,
            _update_avatar=False,
        )

    def test_update_student_unauthorized(self, use_cases, mock_repository):
        """Test updating another user's student raises PermissionError"""
        student_id = uuid4()
        user_id = uuid4()
        request = StudentUpdateRequest(name="New Name")

        # Mock student with different user_id
        mock_student = StudentProfile(
            id=student_id, user_id=uuid4(), name="Test", school="Test", grade="1st"
        )
        mock_repository.get_by_id.return_value = mock_student

        with pytest.raises(PermissionError, match="Access denied"):
            use_cases.update_student(student_id, user_id, request)

    def test_update_student_not_found(self, use_cases, mock_repository):
        """Test updating non-existent student raises ValueError"""
        student_id = uuid4()
        user_id = uuid4()
        request = StudentUpdateRequest(name="New Name")

        mock_repository.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Student not found"):
            use_cases.update_student(student_id, user_id, request)

    def test_delete_student_success(self, use_cases, mock_repository):
        """Test successful student deletion"""
        student_id = uuid4()
        user_id = uuid4()

        mock_repository.verify_ownership.return_value = True
        mock_repository.delete.return_value = True

        result = use_cases.delete_student(student_id, user_id)

        assert result is True
        mock_repository.verify_ownership.assert_called_once_with(student_id, user_id)
        mock_repository.delete.assert_called_once_with(student_id)

    def test_delete_student_unauthorized(self, use_cases, mock_repository):
        """Test deleting another user's student raises PermissionError"""
        student_id = uuid4()
        user_id = uuid4()

        mock_repository.verify_ownership.return_value = False

        with pytest.raises(PermissionError, match="Access denied"):
            use_cases.delete_student(student_id, user_id)

    def test_delete_student_not_found(self, use_cases, mock_repository):
        """Test deleting non-existent student raises ValueError"""
        student_id = uuid4()
        user_id = uuid4()

        mock_repository.verify_ownership.return_value = True
        mock_repository.delete.return_value = False

        with pytest.raises(ValueError, match="Student not found"):
            use_cases.delete_student(student_id, user_id)
