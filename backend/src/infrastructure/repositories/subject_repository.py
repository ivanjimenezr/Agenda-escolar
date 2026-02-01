"""
Subject Repository

Data access layer for Subject entity
"""

from datetime import datetime, time
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.domain.models import Subject, SubjectType, Weekday


class SubjectRepository:
    """Repository for subject data access"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        student_id: UUID,
        name: str,
        days: List[Weekday],
        time: time,
        teacher: str,
        color: str,
        type: SubjectType
    ) -> Subject:
        """Create a new subject

        Raises:
            ValueError: If validation fails
        """
        subject = Subject(
            student_id=student_id,
            name=name,
            days=days,
            time=time,
            teacher=teacher,
            color=color,
            type=type
        )
        self.db.add(subject)
        try:
            self.db.commit()
            self.db.refresh(subject)
            return subject
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to create subject: {str(e)}")

    def get_by_id(self, subject_id: UUID) -> Optional[Subject]:
        """Get subject by ID (excludes soft-deleted)"""
        return self.db.query(Subject).filter(
            Subject.id == subject_id,
            Subject.deleted_at.is_(None)
        ).first()

    def get_by_student_id(
        self,
        student_id: UUID
    ) -> List[Subject]:
        """Get all subjects for a student (excludes soft-deleted)

        Args:
            student_id: UUID of the student

        Returns:
            List of subjects ordered by name
        """
        query = self.db.query(Subject).filter(
            Subject.student_id == student_id,
            Subject.deleted_at.is_(None)
        )

        return query.order_by(Subject.name).all()

    def update(
        self,
        subject_id: UUID,
        name: Optional[str] = None,
        days: Optional[List[Weekday]] = None,
        time: Optional[time] = None,
        teacher: Optional[str] = None,
        color: Optional[str] = None,
        type: Optional[SubjectType] = None
    ) -> Optional[Subject]:
        """Update subject"""
        subject = self.get_by_id(subject_id)
        if not subject:
            return None

        if name is not None:
            subject.name = name
        if days is not None:
            subject.days = days
        if time is not None:
            subject.time = time
        if teacher is not None:
            subject.teacher = teacher
        if color is not None:
            subject.color = color
        if type is not None:
            subject.type = type

        subject.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(subject)
        return subject

    def delete(self, subject_id: UUID) -> bool:
        """Soft delete a subject"""
        subject = self.get_by_id(subject_id)
        if not subject:
            return False

        subject.deleted_at = datetime.utcnow()
        self.db.commit()
        return True
