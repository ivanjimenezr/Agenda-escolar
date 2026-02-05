"""
Subject Use Cases

Business logic for subject operations
"""

from typing import List
from uuid import UUID

from src.application.schemas.subject import SubjectCreateRequest, SubjectUpdateRequest
from src.domain.models import Subject
from src.infrastructure.repositories.student_repository import StudentRepository
from src.infrastructure.repositories.subject_repository import SubjectRepository


class SubjectUseCases:
    """Use cases for subject management"""

    def __init__(self, subject_repo: SubjectRepository, student_repo: StudentRepository):
        self.subject_repo = subject_repo
        self.student_repo = student_repo

    def create_subject(self, user_id: UUID, data: SubjectCreateRequest, replace: bool = False) -> Subject:
        """Create a new subject for a student

        Args:
            user_id: ID of the user creating the subject
            data: Subject creation data
            replace: If True, replace existing conflicting subject(s)

        Returns:
            Created Subject

        Raises:
            ValueError: If validation fails
            PermissionError: If user doesn't own the student
        """
        # Verify student ownership
        if not self.student_repo.verify_ownership(data.student_id, user_id):
            raise PermissionError("Access denied: Student does not belong to user")

        return self.subject_repo.create(
            student_id=data.student_id,
            name=data.name,
            days=data.days,
            time=data.time,
            teacher=data.teacher,
            color=data.color,
            type=data.type,
            replace=replace,
        )

    def get_subject_by_id(self, subject_id: UUID, user_id: UUID) -> Subject:
        """Get a subject by ID

        Args:
            subject_id: ID of the subject
            user_id: ID of the requesting user

        Returns:
            Subject

        Raises:
            ValueError: If subject not found
            PermissionError: If user doesn't own the student
        """
        subject = self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise ValueError("Subject not found")

        # Verify student ownership
        if not self.student_repo.verify_ownership(subject.student_id, user_id):
            raise PermissionError("Access denied")

        return subject

    def get_subjects_by_student(self, student_id: UUID, user_id: UUID) -> List[Subject]:
        """Get all subjects for a student

        Args:
            student_id: ID of the student
            user_id: ID of the requesting user

        Returns:
            List of Subject objects

        Raises:
            PermissionError: If user doesn't own the student
        """
        # Verify student ownership
        if not self.student_repo.verify_ownership(student_id, user_id):
            raise PermissionError("Access denied")

        return self.subject_repo.get_by_student_id(student_id=student_id)

    def update_subject(self, subject_id: UUID, user_id: UUID, data: SubjectUpdateRequest) -> Subject:
        """Update a subject

        Args:
            subject_id: ID of the subject
            user_id: ID of the requesting user
            data: Update data

        Returns:
            Updated Subject

        Raises:
            ValueError: If subject not found
            PermissionError: If user doesn't own the student
        """
        # Get subject and verify ownership
        subject = self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise ValueError("Subject not found")

        if not self.student_repo.verify_ownership(subject.student_id, user_id):
            raise PermissionError("Access denied")

        # Get only fields that were explicitly set in the request
        update_data_dict = data.model_dump(exclude_unset=True)

        updated = self.subject_repo.update(
            subject_id=subject_id,
            name=update_data_dict.get("name") if "name" in update_data_dict else ...,
            days=update_data_dict.get("days") if "days" in update_data_dict else ...,
            time=update_data_dict.get("time") if "time" in update_data_dict else ...,
            teacher=update_data_dict.get("teacher") if "teacher" in update_data_dict else ...,
            color=update_data_dict.get("color") if "color" in update_data_dict else ...,
            type=update_data_dict.get("type") if "type" in update_data_dict else ...,
        )

        if not updated:
            raise ValueError("Subject not found")

        return updated

    def delete_subject(self, subject_id: UUID, user_id: UUID) -> bool:
        """Delete a subject

        Args:
            subject_id: ID of the subject
            user_id: ID of the requesting user

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If subject not found
            PermissionError: If user doesn't own the student
        """
        # Get subject and verify ownership
        subject = self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise ValueError("Subject not found")

        if not self.student_repo.verify_ownership(subject.student_id, user_id):
            raise PermissionError("Access denied")

        result = self.subject_repo.delete(subject_id)

        if not result:
            raise ValueError("Subject not found")

        return True
