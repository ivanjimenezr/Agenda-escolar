"""
Active Modules Use Cases

Business logic for active modules operations
"""

from uuid import UUID

from src.application.schemas.active_modules import ActiveModulesUpdateRequest
from src.domain.models import ActiveModule
from src.infrastructure.repositories.active_modules_repository import ActiveModulesRepository
from src.infrastructure.repositories.student_repository import StudentRepository


class ActiveModulesUseCases:
    """Use cases for active modules management"""

    def __init__(
        self,
        active_modules_repo: ActiveModulesRepository,
        student_repo: StudentRepository
    ):
        self.active_modules_repo = active_modules_repo
        self.student_repo = student_repo

    def get_active_modules(
        self,
        student_id: UUID,
        user_id: UUID
    ) -> ActiveModule:
        """Get active modules configuration for a student

        Args:
            student_id: ID of the student
            user_id: ID of the requesting user

        Returns:
            ActiveModule configuration

        Raises:
            ValueError: If student not found
            PermissionError: If user doesn't own the student
        """
        # Verify student exists and user has permission
        if not self.student_repo.verify_ownership(student_id, user_id):
            raise PermissionError("Access denied")

        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise ValueError("Student not found")

        # Get or create active modules configuration
        return self.active_modules_repo.get_or_create(student_id)

    def update_active_modules(
        self,
        student_id: UUID,
        user_id: UUID,
        data: ActiveModulesUpdateRequest
    ) -> ActiveModule:
        """Update active modules configuration for a student

        Args:
            student_id: ID of the student
            user_id: ID of the requesting user
            data: Active modules update data

        Returns:
            Updated ActiveModule configuration

        Raises:
            ValueError: If student not found
            PermissionError: If user doesn't own the student
        """
        # Verify student exists and user has permission
        if not self.student_repo.verify_ownership(student_id, user_id):
            raise PermissionError("Access denied")

        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise ValueError("Student not found")

        # Update active modules
        updated = self.active_modules_repo.update(
            student_id=student_id,
            subjects=data.subjects,
            exams=data.exams,
            menu=data.menu,
            events=data.events,
            dinner=data.dinner,
            contacts=data.contacts
        )

        if not updated:
            raise ValueError("Failed to update active modules")

        return updated
