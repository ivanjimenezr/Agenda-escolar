"""
Unit tests for Menu Update functionality

These tests specifically focus on the update operation with various
field combinations, especially the date field which was causing issues.
"""

import pytest
from datetime import date, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session

from src.domain.models import StudentProfile, User, MenuItem
from src.infrastructure.repositories.menu_repository import MenuRepository
from src.application.use_cases.menu_use_cases import MenuUseCases
from src.application.schemas.menu import MenuItemUpdateRequest
from src.infrastructure.repositories.student_repository import StudentRepository


@pytest.fixture
def sample_user(db_session: Session):
    """Create a sample user for testing"""
    user = User(
        email="testmenuupdate@example.com",
        name="Test Menu Update User",
        password_hash="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_student(db_session: Session, sample_user: User):
    """Create a sample student for testing"""
    student = StudentProfile(
        user_id=sample_user.id,
        name="Test Student Menu Update",
        school="Test School",
        grade="5th Grade"
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


@pytest.fixture
def menu_use_cases(db_session: Session):
    """Create MenuUseCases instance"""
    menu_repo = MenuRepository(db_session)
    student_repo = StudentRepository(db_session)
    return MenuUseCases(menu_repo, student_repo)


class TestMenuUpdate:
    """Test suite for menu update operations"""

    def test_update_menu_with_date_filled(self, db_session: Session, sample_student: StudentProfile, sample_user: User, menu_use_cases: MenuUseCases):
        """Test updating a menu when date field is filled - this was the failing case"""
        # Create initial menu
        repo = MenuRepository(db_session)
        menu = repo.create(
            student_id=sample_student.id,
            date=date.today(),
            first_course="Lentejas",
            second_course="Pollo asado",
            side_dish="Ensalada",
            dessert="Fruta",
            allergens=["gluten"]
        )

        # Update with date field filled
        new_date = date.today() + timedelta(days=1)
        update_data = MenuItemUpdateRequest(
            date=new_date,
            first_course="Arroz con tomate",
            second_course="Merluza al horno"
        )

        updated = menu_use_cases.update_menu_item(
            menu_id=menu.id,
            user_id=sample_user.id,
            data=update_data
        )

        assert updated.date == new_date
        assert updated.first_course == "Arroz con tomate"
        assert updated.second_course == "Merluza al horno"
        # Unchanged fields
        assert updated.side_dish == "Ensalada"
        assert updated.dessert == "Fruta"

    def test_update_menu_date_from_string(self, db_session: Session, sample_student: StudentProfile):
        """Test updating menu with date as string (as received from frontend)"""
        repo = MenuRepository(db_session)

        menu = repo.create(
            student_id=sample_student.id,
            date=date.today(),
            first_course="Pasta",
            second_course="Pollo",
            allergens=[]
        )

        # Simulate frontend sending date as string
        from pydantic import ValidationError

        try:
            new_date_str = (date.today() + timedelta(days=2)).isoformat()
            update_data = MenuItemUpdateRequest(
                date=new_date_str  # String format "YYYY-MM-DD"
            )

            # The validator should parse this
            assert isinstance(update_data.date, date)

            # Update via repository
            updated = repo.update(
                menu_id=menu.id,
                date=update_data.date
            )

            assert updated.date == date.today() + timedelta(days=2)
        except ValidationError as e:
            pytest.fail(f"Failed to parse date string: {e}")

    def test_update_menu_date_only(self, db_session: Session, sample_student: StudentProfile, sample_user: User, menu_use_cases: MenuUseCases):
        """Test updating ONLY the date field"""
        repo = MenuRepository(db_session)

        menu = repo.create(
            student_id=sample_student.id,
            date=date.today(),
            first_course="Sopa",
            second_course="Carne",
            side_dish="Patatas",
            dessert="Yogur",
            allergens=["lactose"]
        )

        # Update ONLY date
        new_date = date.today() + timedelta(days=5)
        update_data = MenuItemUpdateRequest(
            date=new_date
        )

        updated = menu_use_cases.update_menu_item(
            menu_id=menu.id,
            user_id=sample_user.id,
            data=update_data
        )

        # Only date should change
        assert updated.date == new_date
        # Everything else unchanged
        assert updated.first_course == "Sopa"
        assert updated.second_course == "Carne"
        assert updated.side_dish == "Patatas"
        assert updated.dessert == "Yogur"
        assert updated.allergens == ["lactose"]

    def test_update_menu_without_date(self, db_session: Session, sample_student: StudentProfile, sample_user: User, menu_use_cases: MenuUseCases):
        """Test updating menu without touching date field"""
        repo = MenuRepository(db_session)
        original_date = date.today()

        menu = repo.create(
            student_id=sample_student.id,
            date=original_date,
            first_course="Original First",
            second_course="Original Second",
            allergens=[]
        )

        # Update without date field
        update_data = MenuItemUpdateRequest(
            first_course="Updated First",
            second_course="Updated Second"
        )

        updated = menu_use_cases.update_menu_item(
            menu_id=menu.id,
            user_id=sample_user.id,
            data=update_data
        )

        # Date should remain unchanged
        assert updated.date == original_date
        # Other fields updated
        assert updated.first_course == "Updated First"
        assert updated.second_course == "Updated Second"

    def test_update_menu_with_date_none(self, db_session: Session, sample_student: StudentProfile):
        """Test updating menu with date=None explicitly"""
        repo = MenuRepository(db_session)
        original_date = date.today()

        menu = repo.create(
            student_id=sample_student.id,
            date=original_date,
            first_course="Test",
            second_course="Menu",
            allergens=[]
        )

        # Update with date=None (should not change)
        update_data = MenuItemUpdateRequest(
            first_course="Updated",
            date=None  # Explicitly None
        )

        # date=None should mean "don't change it"
        updated = repo.update(
            menu_id=menu.id,
            first_course=update_data.first_course,
            date=update_data.date
        )

        # date=None should mean "don't change it"
        assert updated.date == original_date
        assert updated.first_course == "Updated"

    def test_update_menu_all_fields_including_date(self, db_session: Session, sample_student: StudentProfile, sample_user: User, menu_use_cases: MenuUseCases):
        """Test updating ALL fields including date"""
        repo = MenuRepository(db_session)

        menu = repo.create(
            student_id=sample_student.id,
            date=date.today(),
            first_course="Old First",
            second_course="Old Second",
            side_dish="Old Side",
            dessert="Old Dessert",
            allergens=["old"]
        )

        # Update everything
        new_date = date.today() + timedelta(days=7)
        update_data = MenuItemUpdateRequest(
            date=new_date,
            first_course="New First",
            second_course="New Second",
            side_dish="New Side",
            dessert="New Dessert",
            allergens=["new", "allergen"]
        )

        updated = menu_use_cases.update_menu_item(
            menu_id=menu.id,
            user_id=sample_user.id,
            data=update_data
        )

        assert updated.date == new_date
        assert updated.first_course == "New First"
        assert updated.second_course == "New Second"
        assert updated.side_dish == "New Side"
        assert updated.dessert == "New Dessert"
        assert updated.allergens == ["new", "allergen"]

    def test_update_menu_date_with_various_formats(self, db_session: Session, sample_student: StudentProfile):
        """Test date field accepts various string formats"""
        repo = MenuRepository(db_session)

        menu = repo.create(
            student_id=sample_student.id,
            date=date.today(),
            first_course="Test",
            second_course="Test",
            allergens=[]
        )

        # Test ISO format YYYY-MM-DD
        update_data1 = MenuItemUpdateRequest(date="2025-12-25")
        assert update_data1.date == date(2025, 12, 25)

        # Test with date object directly
        test_date = date(2025, 6, 15)
        update_data2 = MenuItemUpdateRequest(date=test_date)
        assert update_data2.date == test_date

    def test_update_menu_repository_level(self, db_session: Session, sample_student: StudentProfile):
        """Test update at repository level with date"""
        repo = MenuRepository(db_session)

        menu = repo.create(
            student_id=sample_student.id,
            date=date.today(),
            first_course="Repo Test",
            second_course="Test",
            allergens=[]
        )

        # Update via repository
        new_date = date.today() + timedelta(days=3)
        updated = repo.update(
            menu_id=menu.id,
            date=new_date,
            first_course="Updated Repo Test"
        )

        assert updated.date == new_date
        assert updated.first_course == "Updated Repo Test"
        # Others unchanged
        assert updated.second_course == "Test"

    def test_update_menu_date_edge_cases(self, db_session: Session, sample_student: StudentProfile):
        """Test edge cases for date values"""
        repo = MenuRepository(db_session)

        menu = repo.create(
            student_id=sample_student.id,
            date=date.today(),
            first_course="Edge Case Test",
            second_course="Test",
            allergens=[]
        )

        # Past date
        update_data1 = MenuItemUpdateRequest(date=date(2020, 1, 1))
        assert update_data1.date == date(2020, 1, 1)

        # Future date
        update_data2 = MenuItemUpdateRequest(date=date(2030, 12, 31))
        assert update_data2.date == date(2030, 12, 31)

        # Leap year
        update_data3 = MenuItemUpdateRequest(date=date(2024, 2, 29))
        assert update_data3.date == date(2024, 2, 29)

    def test_update_menu_clear_optional_fields(self, db_session: Session, sample_student: StudentProfile, sample_user: User, menu_use_cases: MenuUseCases):
        """Test clearing optional fields (side_dish, dessert)"""
        repo = MenuRepository(db_session)

        menu = repo.create(
            student_id=sample_student.id,
            date=date.today(),
            first_course="First",
            second_course="Second",
            side_dish="To Remove",
            dessert="To Remove",
            allergens=[]
        )

        # Update with None for optional fields
        update_data = MenuItemUpdateRequest(
            side_dish=None,
            dessert=None
        )

        updated = menu_use_cases.update_menu_item(
            menu_id=menu.id,
            user_id=sample_user.id,
            data=update_data
        )

        # Optional fields should be None
        assert updated.side_dish is None
        assert updated.dessert is None
        # Required fields unchanged
        assert updated.first_course == "First"
        assert updated.second_course == "Second"

    def test_update_menu_allergens_list(self, db_session: Session, sample_student: StudentProfile, sample_user: User, menu_use_cases: MenuUseCases):
        """Test updating allergens list"""
        repo = MenuRepository(db_session)

        menu = repo.create(
            student_id=sample_student.id,
            date=date.today(),
            first_course="Test",
            second_course="Test",
            allergens=["gluten"]
        )

        # Update allergens
        update_data = MenuItemUpdateRequest(
            allergens=["gluten", "lactose", "eggs"]
        )

        updated = menu_use_cases.update_menu_item(
            menu_id=menu.id,
            user_id=sample_user.id,
            data=update_data
        )

        assert len(updated.allergens) == 3
        assert "gluten" in updated.allergens
        assert "lactose" in updated.allergens
        assert "eggs" in updated.allergens

    def test_update_menu_empty_allergens(self, db_session: Session, sample_student: StudentProfile, sample_user: User, menu_use_cases: MenuUseCases):
        """Test updating with empty allergens list"""
        repo = MenuRepository(db_session)

        menu = repo.create(
            student_id=sample_student.id,
            date=date.today(),
            first_course="Test",
            second_course="Test",
            allergens=["gluten", "lactose"]
        )

        # Clear allergens
        update_data = MenuItemUpdateRequest(
            allergens=[]
        )

        updated = menu_use_cases.update_menu_item(
            menu_id=menu.id,
            user_id=sample_user.id,
            data=update_data
        )

        assert updated.allergens == []

    def test_update_multiple_menus_same_date_different_students(self, db_session: Session, sample_user: User, menu_use_cases: MenuUseCases):
        """Test updating multiple menus with same date for different students"""
        # Create two students
        student1 = StudentProfile(
            user_id=sample_user.id,
            name="Student 1",
            school="School",
            grade="5th"
        )
        student2 = StudentProfile(
            user_id=sample_user.id,
            name="Student 2",
            school="School",
            grade="6th"
        )
        db_session.add_all([student1, student2])
        db_session.commit()
        db_session.refresh(student1)
        db_session.refresh(student2)

        repo = MenuRepository(db_session)
        today = date.today()

        # Create menus for both students
        menu1 = repo.create(
            student_id=student1.id,
            date=today,
            first_course="Menu 1",
            second_course="Test",
            allergens=[]
        )

        menu2 = repo.create(
            student_id=student2.id,
            date=today,
            first_course="Menu 2",
            second_course="Test",
            allergens=[]
        )

        # Update both to same new date
        new_date = today + timedelta(days=1)

        updated1 = menu_use_cases.update_menu_item(
            menu_id=menu1.id,
            user_id=sample_user.id,
            data=MenuItemUpdateRequest(date=new_date)
        )

        updated2 = menu_use_cases.update_menu_item(
            menu_id=menu2.id,
            user_id=sample_user.id,
            data=MenuItemUpdateRequest(date=new_date)
        )

        assert updated1.date == new_date
        assert updated2.date == new_date
        # Different students can have same date
        assert updated1.student_id != updated2.student_id
