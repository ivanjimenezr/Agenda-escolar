"""
Active Modules Repository

Data access layer for ActiveModule entity
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.domain.models import ActiveModule


class ActiveModulesRepository:
    """Repository for active modules data access"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_student_id(self, student_id: UUID) -> Optional[ActiveModule]:
        """Get active modules configuration for a student"""
        return self.db.query(ActiveModule).filter(ActiveModule.student_id == student_id).first()

    def create(self, student_id: UUID) -> ActiveModule:
        """Create default active modules configuration for a student"""
        active_modules = ActiveModule(
            student_id=student_id, subjects=True, exams=True, menu=True, events=True, dinner=True, contacts=True
        )
        self.db.add(active_modules)
        self.db.commit()
        self.db.refresh(active_modules)
        return active_modules

    def update(
        self,
        student_id: UUID,
        subjects: Optional[bool] = None,
        exams: Optional[bool] = None,
        menu: Optional[bool] = None,
        events: Optional[bool] = None,
        dinner: Optional[bool] = None,
        contacts: Optional[bool] = None,
    ) -> Optional[ActiveModule]:
        """Update active modules configuration"""
        active_modules = self.get_by_student_id(student_id)

        # If doesn't exist, create it first
        if not active_modules:
            active_modules = self.create(student_id)

        # Update only provided fields
        if subjects is not None:
            active_modules.subjects = subjects
        if exams is not None:
            active_modules.exams = exams
        if menu is not None:
            active_modules.menu = menu
        if events is not None:
            active_modules.events = events
        if dinner is not None:
            active_modules.dinner = dinner
        if contacts is not None:
            active_modules.contacts = contacts

        active_modules.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(active_modules)
        return active_modules

    def get_or_create(self, student_id: UUID) -> ActiveModule:
        """Get active modules or create default if doesn't exist"""
        active_modules = self.get_by_student_id(student_id)
        if not active_modules:
            active_modules = self.create(student_id)
        return active_modules
