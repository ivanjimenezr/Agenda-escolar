"""
Dinner Use Cases

Business logic for dinner operations including AI-powered suggestions
"""

from datetime import date, timedelta
from typing import List, Dict, Any
from uuid import UUID

from src.application.schemas.dinner import (
    DinnerGenerateRequest,
    DinnerCreateRequest,
    DinnerUpdateRequest,
    ShoppingListRequest
)
from src.domain.models import Dinner
from src.infrastructure.repositories.dinner_repository import DinnerRepository
from src.infrastructure.repositories.menu_repository import MenuRepository
from src.infrastructure.repositories.student_repository import StudentRepository
from src.infrastructure.services.gemini_service import GeminiService


class DinnerUseCases:
    """Use cases for dinner management"""

    def __init__(
        self,
        dinner_repo: DinnerRepository,
        menu_repo: MenuRepository,
        student_repo: StudentRepository,
        gemini_service: GeminiService
    ):
        self.dinner_repo = dinner_repo
        self.menu_repo = menu_repo
        self.student_repo = student_repo
        self.gemini_service = gemini_service

    def _verify_student_ownership(self, student_id: UUID, user_id: UUID) -> None:
        """Verify student ownership and existence"""
        if not self.student_repo.verify_ownership(student_id, user_id):
            raise PermissionError("Access denied")

        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise ValueError("Student not found")

    def _get_week_menus(
        self,
        student_id: UUID,
        target_date: date
    ) -> List[Dict[str, Any]]:
        """Get school menus for the current week (Monday to Friday)"""
        # Find the Monday of the week containing target_date
        days_since_monday = target_date.weekday()  # 0 = Monday, 6 = Sunday
        monday = target_date - timedelta(days=days_since_monday)
        friday = monday + timedelta(days=4)

        # Get menus for the week
        menus = self.menu_repo.get_by_student_id(
            student_id=student_id,
            start_date=monday,
            end_date=friday
        )

        # Convert to dict format for AI service
        return [
            {
                'date': menu.date.strftime('%Y-%m-%d'),
                'first_course': menu.first_course,
                'second_course': menu.second_course,
                'side_dish': menu.side_dish,
                'dessert': menu.dessert
            }
            for menu in menus
        ]

    async def generate_dinner_suggestions(
        self,
        student_id: UUID,
        user_id: UUID,
        data: DinnerGenerateRequest
    ) -> List[Dinner]:
        """
        Generate dinner suggestions using AI

        Args:
            student_id: ID of the student
            user_id: ID of the requesting user
            data: Generation parameters (today or week)

        Returns:
            List of created Dinner objects

        Raises:
            ValueError: If student not found or invalid parameters
            PermissionError: If user doesn't own the student
        """
        # Verify ownership and get student
        self._verify_student_ownership(student_id, user_id)
        student = self.student_repo.get_by_id(student_id)

        # Determine target date
        target_date = data.target_date if data.target_date else date.today()

        # Get student's dietary restrictions
        allergies = student.allergies or []
        excluded_foods = student.excluded_foods or []

        dinners = []

        if data.generation_type == "today":
            # Generate for a single day
            week_menus = self._get_week_menus(student_id, target_date)
            school_menu_for_day = self.menu_repo.get_by_date(student_id, target_date)

            # Convert to dict if exists
            menu_dict = None
            if school_menu_for_day:
                menu_dict = {
                    'date': school_menu_for_day.date.strftime('%Y-%m-%d'),
                    'first_course': school_menu_for_day.first_course,
                    'second_course': school_menu_for_day.second_course,
                    'side_dish': school_menu_for_day.side_dish,
                    'dessert': school_menu_for_day.dessert
                }

            # Call AI service
            suggestion = await self.gemini_service.suggest_dinner_for_day(
                target_date=target_date,
                school_menu=menu_dict,
                week_menus=week_menus,
                allergies=allergies,
                excluded_foods=excluded_foods
            )

            # Create or update dinner
            dinner = self.dinner_repo.create_or_update(
                student_id=student_id,
                date=target_date,
                meal=suggestion['meal'],
                ingredients=suggestion.get('ingredients', [])
            )
            dinners.append(dinner)

        elif data.generation_type == "week":
            # Generate for a week (next 7 days from target_date)
            start_date = target_date
            days = 7

            # Get all menus for the period
            end_date = start_date + timedelta(days=days - 1)
            school_menus = self.menu_repo.get_by_student_id(
                student_id=student_id,
                start_date=start_date,
                end_date=end_date
            )

            # Convert to list of dicts
            menus_list = [
                {
                    'date': menu.date.strftime('%Y-%m-%d'),
                    'first_course': menu.first_course,
                    'second_course': menu.second_course,
                    'side_dish': menu.side_dish,
                    'dessert': menu.dessert
                }
                for menu in school_menus
            ]

            # Call AI service for weekly plan
            suggestions = await self.gemini_service.suggest_dinners_for_week(
                start_date=start_date,
                days=days,
                school_menus=menus_list,
                allergies=allergies,
                excluded_foods=excluded_foods
            )

            # Create or update dinners
            for suggestion in suggestions:
                dinner_date = date.fromisoformat(suggestion['date'])
                dinner = self.dinner_repo.create_or_update(
                    student_id=student_id,
                    date=dinner_date,
                    meal=suggestion['meal'],
                    ingredients=suggestion.get('ingredients', [])
                )
                dinners.append(dinner)

        return dinners

    def create_dinner(
        self,
        student_id: UUID,
        user_id: UUID,
        data: DinnerCreateRequest
    ) -> Dinner:
        """
        Create a dinner manually

        Args:
            student_id: ID of the student
            user_id: ID of the requesting user
            data: Dinner data

        Returns:
            Created Dinner object

        Raises:
            ValueError: If student not found
            PermissionError: If user doesn't own the student
        """
        self._verify_student_ownership(student_id, user_id)

        return self.dinner_repo.create(
            student_id=student_id,
            date=data.date,
            meal=data.meal,
            ingredients=data.ingredients
        )

    def get_dinners_for_student(
        self,
        student_id: UUID,
        user_id: UUID,
        start_date: date = None,
        end_date: date = None
    ) -> List[Dinner]:
        """
        Get dinners for a student

        Args:
            student_id: ID of the student
            user_id: ID of the requesting user
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of Dinner objects

        Raises:
            ValueError: If student not found
            PermissionError: If user doesn't own the student
        """
        self._verify_student_ownership(student_id, user_id)

        if start_date and end_date:
            return self.dinner_repo.get_by_student_and_date_range(
                student_id=student_id,
                start_date=start_date,
                end_date=end_date
            )
        else:
            return self.dinner_repo.get_by_student_id(student_id)

    def update_dinner(
        self,
        dinner_id: UUID,
        student_id: UUID,
        user_id: UUID,
        data: DinnerUpdateRequest
    ) -> Dinner:
        """
        Update a dinner

        Args:
            dinner_id: ID of the dinner
            student_id: ID of the student (for verification)
            user_id: ID of the requesting user
            data: Update data

        Returns:
            Updated Dinner object

        Raises:
            ValueError: If dinner or student not found
            PermissionError: If user doesn't own the student or dinner
        """
        self._verify_student_ownership(student_id, user_id)

        # Verify dinner ownership
        if not self.dinner_repo.verify_ownership(dinner_id, student_id):
            raise PermissionError("Access denied to this dinner")

        updated = self.dinner_repo.update(
            dinner_id=dinner_id,
            meal=data.meal,
            ingredients=data.ingredients
        )

        if not updated:
            raise ValueError("Dinner not found")

        return updated

    def delete_dinner(
        self,
        dinner_id: UUID,
        student_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete a dinner

        Args:
            dinner_id: ID of the dinner
            student_id: ID of the student (for verification)
            user_id: ID of the requesting user

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If dinner or student not found
            PermissionError: If user doesn't own the student or dinner
        """
        self._verify_student_ownership(student_id, user_id)

        # Verify dinner ownership
        if not self.dinner_repo.verify_ownership(dinner_id, student_id):
            raise PermissionError("Access denied to this dinner")

        result = self.dinner_repo.delete(dinner_id)

        if not result:
            raise ValueError("Dinner not found")

        return True

    async def generate_shopping_list(
        self,
        student_id: UUID,
        user_id: UUID,
        request: ShoppingListRequest
    ) -> List[Dict[str, Any]]:
        """
        Generate shopping list from dinner plans

        Args:
            student_id: ID of the student
            user_id: ID of the requesting user
            request: Shopping list request parameters

        Returns:
            List of categories with items

        Raises:
            ValueError: If student not found or no dinners found
            PermissionError: If user doesn't own the student
        """
        self._verify_student_ownership(student_id, user_id)

        # Determine date range
        today = date.today()

        if request.scope == "today":
            dinners = self.dinner_repo.get_by_student_and_date_range(
                student_id=student_id,
                start_date=today,
                end_date=today
            )
        elif request.scope == "week":
            end_date = today + timedelta(days=6)
            dinners = self.dinner_repo.get_by_student_and_date_range(
                student_id=student_id,
                start_date=today,
                end_date=end_date
            )
        elif request.scope == "custom":
            if not request.start_date or not request.end_date:
                raise ValueError("start_date and end_date required for custom scope")

            dinners = self.dinner_repo.get_by_student_and_date_range(
                student_id=student_id,
                start_date=request.start_date,
                end_date=request.end_date
            )
        else:
            raise ValueError("Invalid scope")

        if not dinners:
            raise ValueError("No dinners found for the specified period")

        # Convert dinners to format for AI
        dinners_data = [
            {
                'meal': dinner.meal,
                'ingredients': dinner.ingredients
            }
            for dinner in dinners
        ]

        # Call AI service with number of people
        shopping_list = await self.gemini_service.generate_shopping_list(
            dinners_data,
            num_people=request.num_people
        )

        return shopping_list
