"""
Menu Item Use Cases

Business logic for menu item operations
"""

from datetime import date
from typing import List, Optional
from uuid import UUID

from src.application.schemas.menu import MenuItemCreateRequest, MenuItemUpdateRequest
from src.domain.models import MenuItem
from src.infrastructure.repositories.menu_repository import MenuRepository
from src.infrastructure.repositories.student_repository import StudentRepository


class MenuUseCases:
    """Use cases for menu item management"""

    def __init__(self, menu_repo: MenuRepository, student_repo: StudentRepository):
        self.menu_repo = menu_repo
        self.student_repo = student_repo

    def create_menu_item(self, user_id: UUID, data: MenuItemCreateRequest) -> MenuItem:
        """Create a new menu item for a student

        Args:
            user_id: ID of the user creating the menu
            data: Menu creation data

        Returns:
            Created MenuItem

        Raises:
            ValueError: If validation fails
            PermissionError: If user doesn't own the student
        """
        # Verify student ownership
        if not self.student_repo.verify_ownership(data.student_id, user_id):
            raise PermissionError("Access denied: Student does not belong to user")

        return self.menu_repo.create(
            student_id=data.student_id,
            date=data.date,
            first_course=data.first_course,
            second_course=data.second_course,
            side_dish=data.side_dish,
            dessert=data.dessert,
            allergens=data.allergens,
        )

    def get_menu_item_by_id(self, menu_id: UUID, user_id: UUID) -> MenuItem:
        """Get a menu item by ID

        Args:
            menu_id: ID of the menu item
            user_id: ID of the requesting user

        Returns:
            MenuItem

        Raises:
            ValueError: If menu not found
            PermissionError: If user doesn't own the student
        """
        menu = self.menu_repo.get_by_id(menu_id)
        if not menu:
            raise ValueError("Menu item not found")

        # Verify student ownership
        if not self.student_repo.verify_ownership(menu.student_id, user_id):
            raise PermissionError("Access denied")

        return menu

    def get_menu_items_by_student(
        self, student_id: UUID, user_id: UUID, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[MenuItem]:
        """Get all menu items for a student

        Args:
            student_id: ID of the student
            user_id: ID of the requesting user
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of MenuItem objects

        Raises:
            PermissionError: If user doesn't own the student
        """
        # Verify student ownership
        if not self.student_repo.verify_ownership(student_id, user_id):
            raise PermissionError("Access denied")

        return self.menu_repo.get_by_student_id(student_id=student_id, start_date=start_date, end_date=end_date)

    def update_menu_item(self, menu_id: UUID, user_id: UUID, data: MenuItemUpdateRequest) -> MenuItem:
        """Update a menu item

        Args:
            menu_id: ID of the menu item
            user_id: ID of the requesting user
            data: Update data

        Returns:
            Updated MenuItem

        Raises:
            ValueError: If menu not found
            PermissionError: If user doesn't own the student
        """
        # Get menu and verify ownership
        menu = self.menu_repo.get_by_id(menu_id)
        if not menu:
            raise ValueError("Menu item not found")

        if not self.student_repo.verify_ownership(menu.student_id, user_id):
            raise PermissionError("Access denied")

        # Get only fields that were explicitly set in the request
        update_data_dict = data.model_dump(exclude_unset=True)

        updated = self.menu_repo.update(
            menu_id=menu_id,
            date=update_data_dict.get("date") if "date" in update_data_dict else ...,
            first_course=update_data_dict.get("first_course") if "first_course" in update_data_dict else ...,
            second_course=update_data_dict.get("second_course") if "second_course" in update_data_dict else ...,
            side_dish=update_data_dict.get("side_dish") if "side_dish" in update_data_dict else ...,
            dessert=update_data_dict.get("dessert") if "dessert" in update_data_dict else ...,
            allergens=update_data_dict.get("allergens") if "allergens" in update_data_dict else ...,
        )

        if not updated:
            raise ValueError("Menu item not found")

        return updated

    def delete_menu_item(self, menu_id: UUID, user_id: UUID) -> bool:
        """Delete a menu item

        Args:
            menu_id: ID of the menu item
            user_id: ID of the requesting user

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If menu not found
            PermissionError: If user doesn't own the student
        """
        # Get menu and verify ownership
        menu = self.menu_repo.get_by_id(menu_id)
        if not menu:
            raise ValueError("Menu item not found")

        if not self.student_repo.verify_ownership(menu.student_id, user_id):
            raise PermissionError("Access denied")

        result = self.menu_repo.delete(menu_id)

        if not result:
            raise ValueError("Menu item not found")

        return True

    def upsert_menu_item(
        self,
        user_id: UUID,
        student_id: UUID,
        menu_date: date,
        first_course: str,
        second_course: str,
        side_dish: Optional[str] = None,
        dessert: Optional[str] = None,
        allergens: Optional[List[str]] = None,
    ) -> MenuItem:
        """Create or update menu item for a specific date

        Args:
            user_id: ID of the user
            student_id: ID of the student
            menu_date: Date of the menu
            first_course: First course
            second_course: Second course
            side_dish: Optional side dish
            dessert: Optional dessert
            allergens: Optional list of allergens

        Returns:
            MenuItem (created or updated)

        Raises:
            PermissionError: If user doesn't own the student
        """
        # Verify student ownership
        if not self.student_repo.verify_ownership(student_id, user_id):
            raise PermissionError("Access denied")

        return self.menu_repo.upsert(
            student_id=student_id,
            date=menu_date,
            first_course=first_course,
            second_course=second_course,
            side_dish=side_dish,
            dessert=dessert,
            allergens=allergens,
        )
