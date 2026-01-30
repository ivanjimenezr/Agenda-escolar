"""
Menu Item Repository

Data access layer for MenuItem entity
"""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.domain.models import MenuItem


class MenuRepository:
    """Repository for menu item data access"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        student_id: UUID,
        date: date,
        first_course: str,
        second_course: str,
        side_dish: Optional[str] = None,
        dessert: Optional[str] = None,
        allergens: Optional[List[str]] = None
    ) -> MenuItem:
        """Create a new menu item"""
        menu = MenuItem(
            student_id=student_id,
            date=date,
            first_course=first_course,
            second_course=second_course,
            side_dish=side_dish,
            dessert=dessert,
            allergens=allergens or []
        )
        self.db.add(menu)
        self.db.commit()
        self.db.refresh(menu)
        return menu

    def get_by_id(self, menu_id: UUID) -> Optional[MenuItem]:
        """Get menu item by ID (excludes soft-deleted)"""
        return self.db.query(MenuItem).filter(
            MenuItem.id == menu_id,
            MenuItem.deleted_at.is_(None)
        ).first()

    def get_by_student_id(
        self,
        student_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[MenuItem]:
        """Get all menu items for a student (excludes soft-deleted)

        Args:
            student_id: UUID of the student
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering

        Returns:
            List of menu items ordered by date
        """
        query = self.db.query(MenuItem).filter(
            MenuItem.student_id == student_id,
            MenuItem.deleted_at.is_(None)
        )

        if start_date:
            query = query.filter(MenuItem.date >= start_date)
        if end_date:
            query = query.filter(MenuItem.date <= end_date)

        return query.order_by(MenuItem.date).all()

    def get_by_date(self, student_id: UUID, menu_date: date) -> Optional[MenuItem]:
        """Get menu item by student and date"""
        return self.db.query(MenuItem).filter(
            MenuItem.student_id == student_id,
            MenuItem.date == menu_date,
            MenuItem.deleted_at.is_(None)
        ).first()

    def update(
        self,
        menu_id: UUID,
        date: Optional[date] = None,
        first_course: Optional[str] = None,
        second_course: Optional[str] = None,
        side_dish: Optional[str] = None,
        dessert: Optional[str] = None,
        allergens: Optional[List[str]] = None
    ) -> Optional[MenuItem]:
        """Update menu item"""
        menu = self.get_by_id(menu_id)
        if not menu:
            return None

        if date is not None:
            menu.date = date
        if first_course is not None:
            menu.first_course = first_course
        if second_course is not None:
            menu.second_course = second_course
        if side_dish is not None:
            menu.side_dish = side_dish
        if dessert is not None:
            menu.dessert = dessert
        if allergens is not None:
            menu.allergens = allergens

        menu.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(menu)
        return menu

    def delete(self, menu_id: UUID) -> bool:
        """Soft delete a menu item"""
        menu = self.get_by_id(menu_id)
        if not menu:
            return False

        menu.deleted_at = datetime.utcnow()
        self.db.commit()
        return True

    def upsert(
        self,
        student_id: UUID,
        date: date,
        first_course: str,
        second_course: str,
        side_dish: Optional[str] = None,
        dessert: Optional[str] = None,
        allergens: Optional[List[str]] = None
    ) -> MenuItem:
        """Create or update menu item for a specific date

        If a menu item already exists for the student on the given date,
        it will be updated. Otherwise, a new one will be created.
        """
        existing = self.get_by_date(student_id, date)

        if existing:
            return self.update(
                menu_id=existing.id,
                first_course=first_course,
                second_course=second_course,
                side_dish=side_dish,
                dessert=dessert,
                allergens=allergens
            )
        else:
            return self.create(
                student_id=student_id,
                date=date,
                first_course=first_course,
                second_course=second_course,
                side_dish=side_dish,
                dessert=dessert,
                allergens=allergens
            )
