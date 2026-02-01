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

    def get_conflicting(self, student_id: UUID, days: List[Weekday], time: time) -> List[Subject]:
        """Return existing subjects for the student that overlap at the same time and days.

        Normalize incoming `days` to their enum *values* (e.g. "Lunes") before querying.
        Also accept strings (e.g. 'LUNES' or 'Lunes') and map them to the correct DB value.
        """
        # Normalize days to DB enum textual values
        normalized_days: List[str] = []
        from src.domain.models import Weekday as WeekdayEnum
        for d in days:
            if isinstance(d, WeekdayEnum):
                normalized_days.append(d.value)
                continue
            if isinstance(d, str):
                # Try direct value match (case-sensitive)
                for member in WeekdayEnum:
                    if d == member.value:
                        normalized_days.append(member.value)
                        break
                else:
                    # Try name match / upper-case like 'LUNES'
                    try:
                        member = WeekdayEnum[d.upper()]
                        normalized_days.append(member.value)
                    except Exception:
                        # Fallback: try case-insensitive value match
                        matched = False
                        for member in WeekdayEnum:
                            if d.lower() == member.value.lower():
                                normalized_days.append(member.value)
                                matched = True
                                break
                        if not matched:
                            # Unknown value - let the DB return no conflicts
                            continue
            else:
                # Unknown type - skip
                continue

        if not normalized_days:
            return []

        return self.db.query(Subject).filter(
            Subject.student_id == student_id,
            Subject.time == time,
            Subject.deleted_at.is_(None),
            Subject.days.overlap(normalized_days)
        ).all()

    def delete_conflicting(self, student_id: UUID, days: List[Weekday], time: time) -> List[Subject]:
        """Soft delete conflicting subjects and return them."""
        conflicts = self.get_conflicting(student_id, days, time)
        for c in conflicts:
            c.deleted_at = datetime.utcnow()
        if conflicts:
            self.db.commit()
        return conflicts

    def create(
        self,
        student_id: UUID,
        name: str,
        days: List[Weekday],
        time: time,
        teacher: str,
        color: str,
        type: SubjectType,
        replace: bool = False
    ) -> Subject:
        """Create a new subject

        If a conflicting subject exists and `replace` is False, a ConflictError is raised.
        If `replace` is True, conflicting subjects are soft-deleted and the new subject is created.

        Raises:
            ConflictError: If a conflict is detected and replace is False
            ValueError: If other DB errors occur
        """
        # Check for conflicts
        conflicts = self.get_conflicting(student_id, days, time)
        if conflicts and not replace:
            # Let caller decide how to handle (raise a specific exception with the conflicting items)
            from src.application.exceptions import ConflictError
            raise ConflictError(conflicts=conflicts)

        if conflicts and replace:
            for c in conflicts:
                c.deleted_at = datetime.utcnow()

        # Ensure teacher is not None to avoid DB NOT NULL constraint from older migrations
        teacher_value = teacher if teacher is not None else ""
        subject = Subject(
            student_id=student_id,
            name=name,
            days=days,
            time=time,
            teacher=teacher_value,
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
