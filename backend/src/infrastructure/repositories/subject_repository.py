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

        Normalize incoming `days` robustly to their enum textual *values* (e.g. "Lunes")
        before constructing the query. Accepts:
         - enum members (Weekday.LUNES)
         - enum names ("LUNES")
         - enum values in any case ("lunes", "Lunes")
         - strings with/without accents ("SABADO", "Sábado")
        """
        import unicodedata
        # Helper to remove accents for tolerant matching
        def strip_accents(s: str) -> str:
            return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

        import logging
        logger = logging.getLogger(__name__)

        normalized_days: List[str] = []
        from src.domain.models import Weekday as WeekdayEnum

        for d in days:
            val: Optional[str] = None

            # Enum instance -> use its value directly
            if isinstance(d, WeekdayEnum):
                val = d.value

            # Try string-based matching
            elif isinstance(d, str):
                s = d.strip()
                # 1) direct case-insensitive match against enum values
                for member in WeekdayEnum:
                    if s.lower() == member.value.lower():
                        val = member.value
                        break
                # 2) try matching by enum name, e.g., 'LUNES' using __members__ for safety
                if val is None:
                    member = WeekdayEnum.__members__.get(s.upper())
                    if member is not None:
                        val = member.value
                # 3) accent-insensitive match as a last resort
                if val is None:
                    s_norm = strip_accents(s.lower())
                    for member in WeekdayEnum:
                        if strip_accents(member.value.lower()) == s_norm:
                            val = member.value
                            break

            # If we found a normalized textual value, append
            if val is not None:
                normalized_days.append(val)

        logger.debug("SubjectRepository.get_conflicting - normalized_days: %s (input days: %s)", normalized_days, days)

        # Nothing we can match - avoid querying with invalid values
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
        print("###Asignatura a crear:")
        print(student_id, name, days, time, teacher_value, color, type, replace)
        print(f"Creating subject: {subject}")
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
