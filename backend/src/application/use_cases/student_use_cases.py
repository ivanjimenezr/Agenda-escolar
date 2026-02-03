"""
Student Profile Use Cases

Business logic for student profile operations
"""

from typing import List
from uuid import UUID

from src.application.schemas.student import (
    StudentCreateRequest,
    StudentUpdateRequest
)
from src.domain.models import StudentProfile
from src.infrastructure.repositories.student_repository import StudentRepository


class StudentUseCases:
    """Use cases for student profile management"""

    def __init__(self, student_repo: StudentRepository):
        self.student_repo = student_repo

    def create_student(
        self,
        user_id: UUID,
        data: StudentCreateRequest
    ) -> StudentProfile:
        """Create a new student profile for a user

        Args:
            user_id: ID of the user creating the student
            data: Student creation data

        Returns:
            Created StudentProfile

        Raises:
            ValueError: If validation fails
        """
        return self.student_repo.create(
            user_id=user_id,
            name=data.name,
            school=data.school,
            grade=data.grade,
            avatar_url=data.avatar_url,
            allergies=data.allergies,
            excluded_foods=data.excluded_foods
        )

    def get_student_by_id(
        self,
        student_id: UUID,
        user_id: UUID
    ) -> StudentProfile:
        """Get a student profile by ID

        Args:
            student_id: ID of the student
            user_id: ID of the requesting user

        Returns:
            StudentProfile

        Raises:
            ValueError: If student not found
            PermissionError: If user doesn't own the student
        """
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise ValueError("Student not found")

        # Verify ownership
        if not self.student_repo.verify_ownership(student_id, user_id):
            raise PermissionError("Access denied")

        return student

    def get_students_by_user(self, user_id: UUID) -> List[StudentProfile]:
        """Get all student profiles for a user

        Args:
            user_id: ID of the user

        Returns:
            List of StudentProfile objects
        """
        return self.student_repo.get_by_user_id(user_id)

    def update_student(
        self,
        student_id: UUID,
        user_id: UUID,
        data: StudentUpdateRequest
    ) -> StudentProfile:
        """Update a student profile

        Args:
            student_id: ID of the student
            user_id: ID of the requesting user
            data: Update data

        Returns:
            Updated StudentProfile

        Raises:
            ValueError: If student not found
            PermissionError: If user doesn't own the student
        """
        # Check if student exists first
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise ValueError("Student not found")

        # Verify ownership
        if student.user_id != user_id:
            raise PermissionError("Access denied")

        # Build kwargs - Pydantic sets all fields, so check model_dump(exclude_unset=True)
        update_data_dict = data.model_dump(exclude_unset=True)

        # Pass all updates directly, letting repository handle None values
        updated = self.student_repo.update(
            student_id=student_id,
            name=update_data_dict.get('name'),
            school=update_data_dict.get('school'),
            grade=update_data_dict.get('grade'),
            avatar_url=update_data_dict.get('avatar_url') if 'avatar_url' not in update_data_dict else data.avatar_url,
            allergies=update_data_dict.get('allergies'),
            excluded_foods=update_data_dict.get('excluded_foods'),
            # Pass set_avatar_url flag to indicate explicit update
            _update_avatar=('avatar_url' in update_data_dict)
        )

        return updated

    def delete_student(
        self,
        student_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete a student profile

        Args:
            student_id: ID of the student
            user_id: ID of the requesting user

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If student not found
            PermissionError: If user doesn't own the student
        """
        # Verify ownership
        if not self.student_repo.verify_ownership(student_id, user_id):
            raise PermissionError("Access denied")

        result = self.student_repo.delete(student_id)

        if not result:
            raise ValueError("Student not found")

        return True
