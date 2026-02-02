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

    def _normalize_days(self, days: List[Weekday]) -> List[str]:
        """Normalize a sequence of weekday inputs to their PostgreSQL enum values.

        Accepts enum members, enum names ("LUNES"), values in any case ("lunes"),
        and accent-insensitive strings ("MIERCOLES" / "Miercoles" / "Miércoles").
        Returns a list of valid enum values (e.g., "Monday", "Sábado") suitable for DB queries.
        """
        import unicodedata
        def strip_accents(s: str) -> str:
            return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

        # Import the current Weekday enum from models.py (which uses Spanish names)
        from src.domain.models import Weekday as SpanishWeekdayEnum

        # Define the mapping to the *expected database values*.
        # Assuming DB expects English weekdays and Spanish weekend names as added by migration.
        db_day_values_mapping = {
            "Lunes": "Monday",
            "Martes": "Tuesday",
            "Miércoles": "Wednesday",
            "Jueves": "Thursday",
            "Viernes": "Friday",
            # Weekend days from migration - assume these are the exact values the DB expects.
            "Sábado": "Sábado",
            "Domingo": "Domingo",
        }

        normalized_days: List[str] = []
        for d in days:
            identified_spanish_value: Optional[str] = None

            # 1. If input is the current Python enum instance (Spanish values)
            if isinstance(d, SpanishWeekdayEnum):
                identified_spanish_value = d.value # e.g., "Lunes"

            # 2. Try string-based matching
            elif isinstance(d, str):
                s = d.strip()
                s_lower = s.lower()
                s_upper = s.upper()

                # Try to map from input string to Spanish enum value first
                for spanish_val_key in db_day_values_mapping.keys(): # Iterate through Spanish keys
                    # Case-insensitive match against Spanish value
                    if s_lower == spanish_val_key.lower():
                        identified_spanish_value = spanish_val_key
                        break
                    # Match uppercase Spanish name (like 'LUNES') to get its Spanish value
                    if s_upper == spanish_val_key.upper():
                         identified_spanish_value = spanish_val_key
                         break
                
                # Accent-insensitive match as a last resort for Spanish value
                if identified_spanish_value is None:
                    s_norm = strip_accents(s_lower)
                    for spanish_val_key in db_day_values_mapping.keys():
                        if strip_accents(spanish_val_key.lower()) == s_norm:
                            identified_spanish_value = spanish_val_key
                            break

            # If we successfully identified a Spanish day value, map it to its DB representation
            if identified_spanish_value is not None:
                db_value = db_day_values_mapping.get(identified_spanish_value)
                if db_value: # Ensure mapping exists
                    normalized_days.append(db_value)

        return normalized_days

    def get_conflicting(self, student_id: UUID, days: List[Weekday], time: time) -> List[Subject]:
        """Return existing subjects for the student that overlap at the same time and days.

        Uses `_normalize_days` to produce valid enum textual values for the DB query.
        """
        import logging
        logger = logging.getLogger(__name__)

        normalized_days = self._normalize_days(days)
        logger.debug("SubjectRepository.get_conflicting - normalized_days: %s (input days: %s)", normalized_days, days)

        # Nothing we can match - avoid querying with invalid values
        if not normalized_days:
            return []

        # Detect whether the underlying database supports ARRAY overlap
        supports_overlap = hasattr(Subject.days, 'overlap')

        if supports_overlap:
            # Use native SQL overlap operator (Postgres)
            return self.db.query(Subject).filter(
                Subject.student_id == student_id,
                Subject.time == time,
                Subject.deleted_at.is_(None),
                Subject.days.overlap(normalized_days)
            ).all()
        else:
            # Fallback for SQLite/JSON: fetch candidates and check overlap in Python
            candidates = self.db.query(Subject).filter(
                Subject.student_id == student_id,
                Subject.time == time,
                Subject.deleted_at.is_(None)
            ).all()

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

        # Normalize days to their string values (e.g., "Lunes", "Martes") for DB storage
        # This ensures we always pass the enum VALUE (not NAME) to PostgreSQL
        normalized_days = self._normalize_days(days)

        subject = Subject(
            student_id=student_id,
            name=name,
            days=normalized_days,
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
            # Normalize days to their string values (e.g., "Lunes", "Martes") for DB storage
            subject.days = self._normalize_days(days)
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
