"""
Exam Use Cases

Business logic for exam operations
"""

from datetime import date
from typing import List, Optional
from uuid import UUID

from src.application.schemas.exam import (
    ExamCreateRequest,
    ExamUpdateRequest
)
from src.domain.models import Exam
from src.infrastructure.repositories.exam_repository import ExamRepository
from src.infrastructure.repositories.student_repository import StudentRepository


class ExamUseCases:
    """Use cases for exam management"""

    def __init__(
        self,
        exam_repo: ExamRepository,
        student_repo: StudentRepository
    ):
        self.exam_repo = exam_repo
        self.student_repo = student_repo

    def create_exam(
        self,
        user_id: UUID,
        data: ExamCreateRequest
    ) -> Exam:
        """Create a new exam for a student

        Args:
            user_id: ID of the user creating the exam
            data: Exam creation data

        Returns:
            Created Exam

        Raises:
            ValueError: If validation fails
            PermissionError: If user doesn't own the student
        """
        # Verify student ownership
        if not self.student_repo.verify_ownership(data.student_id, user_id):
            raise PermissionError("Access denied: Student does not belong to user")

        return self.exam_repo.create(
            student_id=data.student_id,
            subject=data.subject,
            date=data.date,
            topic=data.topic,
            notes=data.notes
        )

    def get_exam_by_id(
        self,
        exam_id: UUID,
        user_id: UUID
    ) -> Exam:
        """Get an exam by ID

        Args:
            exam_id: ID of the exam
            user_id: ID of the requesting user

        Returns:
            Exam

        Raises:
            ValueError: If exam not found
            PermissionError: If user doesn't own the student
        """
        exam = self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise ValueError("Exam not found")

        # Verify student ownership
        if not self.student_repo.verify_ownership(exam.student_id, user_id):
            raise PermissionError("Access denied")

        return exam

    def get_exams_by_student(
        self,
        student_id: UUID,
        user_id: UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[Exam]:
        """Get all exams for a student

        Args:
            student_id: ID of the student
            user_id: ID of the requesting user
            from_date: Optional filter - only exams from this date onwards
            to_date: Optional filter - only exams until this date

        Returns:
            List of Exam objects ordered by date

        Raises:
            PermissionError: If user doesn't own the student
        """
        # Verify student ownership
        if not self.student_repo.verify_ownership(student_id, user_id):
            raise PermissionError("Access denied")

        return self.exam_repo.get_by_student_id(
            student_id=student_id,
            from_date=from_date,
            to_date=to_date
        )

    def update_exam(
        self,
        exam_id: UUID,
        user_id: UUID,
        data: ExamUpdateRequest
    ) -> Exam:
        """Update an exam

        Args:
            exam_id: ID of the exam
            user_id: ID of the requesting user
            data: Update data

        Returns:
            Updated Exam

        Raises:
            ValueError: If exam not found
            PermissionError: If user doesn't own the student
        """
        # Get exam and verify ownership
        exam = self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise ValueError("Exam not found")

        if not self.student_repo.verify_ownership(exam.student_id, user_id):
            raise PermissionError("Access denied")

        updated = self.exam_repo.update(
            exam_id=exam_id,
            subject=data.subject,
            date=data.date,
            topic=data.topic,
            notes=data.notes
        )

        if not updated:
            raise ValueError("Exam not found")

        return updated

    def delete_exam(
        self,
        exam_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete an exam (hard delete)

        Args:
            exam_id: ID of the exam
            user_id: ID of the requesting user

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If exam not found
            PermissionError: If user doesn't own the student
        """
        # Get exam and verify ownership
        exam = self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise ValueError("Exam not found")

        if not self.student_repo.verify_ownership(exam.student_id, user_id):
            raise PermissionError("Access denied")

        result = self.exam_repo.delete(exam_id)

        if not result:
            raise ValueError("Exam not found")

        return True
