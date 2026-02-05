"""
Subject Repository

Data access layer for Subject entity
"""

from datetime import datetime, time, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.domain.models import Subject


class SubjectRepository:
    """Repository for subject data access"""

    def __init__(self, db: Session):
        self.db = db

    def _normalize_days(self, days: List[str]) -> List[str]:
        """Normalize weekday strings to title case with proper Spanish accents.

        Args:
            days: List of weekday strings in any case

        Returns:
            List of normalized weekday strings (e.g., "Lunes", "Martes")
        """
        if not days:
            return []

        # Map of normalized day names (lowercase without accents) to proper Spanish format
        valid_days = {
            "lunes": "Lunes",
            "martes": "Martes",
            "miercoles": "Miércoles",
            "miércoles": "Miércoles",
            "jueves": "Jueves",
            "viernes": "Viernes",
            "sabado": "Sábado",
            "sábado": "Sábado",
            "domingo": "Domingo",
        }

        normalized = []
        for day in days:
            if not day:
                continue
            # Normalize to lowercase for lookup
            day_lower = str(day).strip().lower()
            # If it's a valid day, add the properly formatted version
            if day_lower in valid_days:
                normalized.append(valid_days[day_lower])

        return normalized

    def get_conflicting(self, student_id: UUID, days: List[str], time: time) -> List[Subject]:
        """Return existing subjects for the student that overlap at the same time and days.

        Uses `_normalize_days` to clean up the day strings for the DB query.
        """
        import logging

        logger = logging.getLogger(__name__)

        normalized_days = self._normalize_days(days)
        logger.debug("SubjectRepository.get_conflicting - normalized_days: %s (input days: %s)", normalized_days, days)

        # Nothing we can match - avoid querying with invalid values
        if not normalized_days:
            return []

        # Detect whether the underlying database supports ARRAY overlap
        supports_overlap = hasattr(Subject.days, "overlap")

        if supports_overlap:
            # Use native SQL overlap operator (Postgres)
            return (
                self.db.query(Subject)
                .filter(
                    Subject.student_id == student_id,
                    Subject.time == time,
                    Subject.deleted_at.is_(None),
                    Subject.days.overlap(normalized_days),
                )
                .all()
            )
        else:
            # Fallback for SQLite/JSON: fetch candidates and check overlap in Python
            candidates = (
                self.db.query(Subject)
                .filter(Subject.student_id == student_id, Subject.time == time, Subject.deleted_at.is_(None))
                .all()
            )

            result = []
            nd_set = set(normalized_days)
            for s in candidates:
                try:
                    subject_days = set(s.days or [])
                except Exception:
                    subject_days = set()
                if subject_days & nd_set:
                    result.append(s)
            return result

    def delete_conflicting(self, student_id: UUID, days: List[str], time: time) -> List[Subject]:
        """Soft delete conflicting subjects and return them."""
        conflicts = self.get_conflicting(student_id, days, time)
        for c in conflicts:
            c.deleted_at = datetime.now(timezone.utc)
        if conflicts:
            self.db.commit()
        return conflicts

    def create(
        self,
        student_id: UUID,
        name: str,
        days: List[str],
        time: time,
        teacher: str,
        color: str,
        type: str,
        replace: bool = False,
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
                c.deleted_at = datetime.now(timezone.utc)

        # Ensure teacher is not None to avoid DB NOT NULL constraint from older migrations
        teacher_value = teacher if teacher is not None else ""

        # Normalize/clean the days (just strips whitespace now since we use plain strings)
        normalized_days = self._normalize_days(days)

        subject = Subject(
            student_id=student_id,
            name=name,
            days=normalized_days,
            time=time,
            teacher=teacher_value,
            color=color,
            type=type,
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
        return self.db.query(Subject).filter(Subject.id == subject_id, Subject.deleted_at.is_(None)).first()

    def get_by_student_id(self, student_id: UUID) -> List[Subject]:
        """Get all subjects for a student (excludes soft-deleted)

        Args:
            student_id: UUID of the student

        Returns:
            List of subjects ordered by name
        """
        query = self.db.query(Subject).filter(Subject.student_id == student_id, Subject.deleted_at.is_(None))

        return query.order_by(Subject.name).all()

    def update(
        self,
        subject_id: UUID,
        name: Optional[str] = ...,
        days: Optional[List[str]] = ...,
        time: Optional[time] = ...,
        teacher: Optional[str] = ...,
        color: Optional[str] = ...,
        type: Optional[str] = ...,
    ) -> Optional[Subject]:
        """Update subject

        Use Ellipsis (...) as default to distinguish between "not provided" and "set to None"
        """
        subject = self.get_by_id(subject_id)
        if not subject:
            return None

        if name is not ...:
            subject.name = name
        if days is not ...:
            # Clean/normalize the days (just strips whitespace now since we use plain strings)
            subject.days = self._normalize_days(days)
        if time is not ...:
            subject.time = time
        if teacher is not ...:
            subject.teacher = teacher
        if color is not ...:
            subject.color = color
        if type is not ...:
            subject.type = type

        subject.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(subject)
        return subject

    def delete(self, subject_id: UUID) -> bool:
        """Soft delete a subject"""
        subject = self.get_by_id(subject_id)
        if not subject:
            return False

        subject.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        return True
