"""
Exam Repository

Data access layer for Exam entity
"""

from datetime import datetime, date, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.domain.models import Exam


class ExamRepository:
    """Repository for exam data access"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        student_id: UUID,
        subject: str,
        date: date,
        topic: str,
        notes: Optional[str] = None
    ) -> Exam:
        """Create a new exam

        Args:
            student_id: UUID of the student
            subject: Subject name
            date: Exam date
            topic: Exam topic
            notes: Optional notes

        Returns:
            Created Exam

        Raises:
            ValueError: If database error occurs
        """
        exam = Exam(
            student_id=student_id,
            subject=subject,
            date=date,
            topic=topic,
            notes=notes
        )

        self.db.add(exam)
        try:
            self.db.commit()
            self.db.refresh(exam)
            return exam
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to create exam: {str(e)}")

    def get_by_id(self, exam_id: UUID) -> Optional[Exam]:
        """Get exam by ID"""
        return self.db.query(Exam).filter(
            Exam.id == exam_id
        ).first()

    def get_by_student_id(
        self,
        student_id: UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[Exam]:
        """Get all exams for a student

        Args:
            student_id: UUID of the student
            from_date: Optional filter - only exams from this date onwards
            to_date: Optional filter - only exams until this date

        Returns:
            List of exams ordered by date ascending
        """
        query = self.db.query(Exam).filter(
            Exam.student_id == student_id
        )

        if from_date:
            query = query.filter(Exam.date >= from_date)
        if to_date:
            query = query.filter(Exam.date <= to_date)

        return query.order_by(Exam.date.asc()).all()

    def update(
        self,
        exam_id: UUID,
        subject: Optional[str] = None,
        date: Optional[date] = None,
        topic: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[Exam]:
        """Update exam

        Args:
            exam_id: UUID of the exam
            subject: Optional new subject name
            date: Optional new date
            topic: Optional new topic
            notes: Optional new notes

        Returns:
            Updated Exam or None if not found
        """
        exam = self.get_by_id(exam_id)
        if not exam:
            return None

        if subject is not None:
            exam.subject = subject
        if date is not None:
            exam.date = date
        if topic is not None:
            exam.topic = topic
        if notes is not None:
            exam.notes = notes

        exam.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(exam)
        return exam

    def delete(self, exam_id: UUID) -> bool:
        """Hard delete an exam (permanent deletion)

        Args:
            exam_id: UUID of the exam to delete

        Returns:
            True if deleted, False if not found
        """
        exam = self.get_by_id(exam_id)
        if not exam:
            return False

        self.db.delete(exam)
        self.db.commit()
        return True
