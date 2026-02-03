"""
Dinner Repository

Data access layer for Dinner entity
"""

from datetime import datetime, date, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.domain.models import Dinner


class DinnerRepository:
    """Repository for dinner data access"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        student_id: UUID,
        date: date,
        meal: str,
        ingredients: Optional[List[str]] = None
    ) -> Dinner:
        """Create a new dinner"""
        dinner = Dinner(
            student_id=student_id,
            date=date,
            meal=meal,
            ingredients=ingredients or []
        )
        self.db.add(dinner)
        self.db.commit()
        self.db.refresh(dinner)
        return dinner

    def get_by_id(self, dinner_id: UUID) -> Optional[Dinner]:
        """Get dinner by ID (excludes soft-deleted)"""
        return self.db.query(Dinner).filter(
            Dinner.id == dinner_id,
            Dinner.deleted_at.is_(None)
        ).first()

    def get_by_student_id(self, student_id: UUID) -> List[Dinner]:
        """Get all dinners for a student (excludes soft-deleted)"""
        return self.db.query(Dinner).filter(
            Dinner.student_id == student_id,
            Dinner.deleted_at.is_(None)
        ).order_by(Dinner.date.desc()).all()

    def get_by_student_and_date_range(
        self,
        student_id: UUID,
        start_date: date,
        end_date: date
    ) -> List[Dinner]:
        """Get dinners for a student within a date range"""
        return self.db.query(Dinner).filter(
            Dinner.student_id == student_id,
            Dinner.date >= start_date,
            Dinner.date <= end_date,
            Dinner.deleted_at.is_(None)
        ).order_by(Dinner.date).all()

    def get_by_student_and_date(
        self,
        student_id: UUID,
        date: date
    ) -> Optional[Dinner]:
        """Get dinner for a specific student and date"""
        return self.db.query(Dinner).filter(
            Dinner.student_id == student_id,
            Dinner.date == date,
            Dinner.deleted_at.is_(None)
        ).first()

    def update(
        self,
        dinner_id: UUID,
        meal: Optional[str] = None,
        ingredients: Optional[List[str]] = None
    ) -> Optional[Dinner]:
        """Update dinner"""
        dinner = self.get_by_id(dinner_id)
        if not dinner:
            return None

        if meal is not None:
            dinner.meal = meal
        if ingredients is not None:
            dinner.ingredients = ingredients

        dinner.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(dinner)
        return dinner

    def delete(self, dinner_id: UUID) -> bool:
        """Soft delete a dinner"""
        dinner = self.get_by_id(dinner_id)
        if not dinner:
            return False

        dinner.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        return True

    def delete_by_student_and_date(self, student_id: UUID, date: date) -> bool:
        """Delete dinner for a specific date (to replace with new AI suggestion)"""
        dinner = self.get_by_student_and_date(student_id, date)
        if not dinner:
            return False

        dinner.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        return True

    def create_or_update(
        self,
        student_id: UUID,
        date: date,
        meal: str,
        ingredients: Optional[List[str]] = None
    ) -> Dinner:
        """Create or update dinner for a specific date"""
        # Check for existing dinner (including soft-deleted ones)
        existing = self.db.query(Dinner).filter(
            Dinner.student_id == student_id,
            Dinner.date == date
        ).first()

        if existing:
            # Update existing (even if soft-deleted)
            existing.meal = meal
            existing.ingredients = ingredients or []
            existing.deleted_at = None  # Restore if was soft-deleted
            existing.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            return self.create(student_id, date, meal, ingredients)

    def verify_ownership(self, dinner_id: UUID, student_id: UUID) -> bool:
        """Verify that a dinner belongs to a specific student"""
        dinner = self.db.query(Dinner).filter(
            Dinner.id == dinner_id,
            Dinner.deleted_at.is_(None)
        ).first()

        if not dinner:
            return False

        return dinner.student_id == student_id
