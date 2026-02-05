"""
Unit tests for MenuRepository
"""

from datetime import date, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from src.domain.models import MenuItem, StudentProfile, User
from src.infrastructure.repositories.menu_repository import MenuRepository


@pytest.fixture
def sample_user(db_session: Session):
    """Create a sample user for testing"""
    user = User(email="test@example.com", name="Test User", password_hash="hashed_password")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_student(db_session: Session, sample_user: User):
    """Create a sample student for testing"""
    student = StudentProfile(user_id=sample_user.id, name="Test Student", school="Test School", grade="5th Grade")
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


class TestMenuRepository:
    """Test suite for MenuRepository"""

    def test_create_menu_item(self, db_session: Session, sample_student: StudentProfile):
        """Test creating a new menu item"""
        repo = MenuRepository(db_session)
        menu_date = date.today()

        menu = repo.create(
            student_id=sample_student.id,
            date=menu_date,
            first_course="Lentejas",
            second_course="Pollo asado",
            side_dish="Ensalada",
            dessert="Fruta",
            allergens=["gluten"],
        )

        assert menu.id is not None
        assert menu.student_id == sample_student.id
        assert menu.date == menu_date
        assert menu.first_course == "Lentejas"
        assert menu.second_course == "Pollo asado"
        assert menu.side_dish == "Ensalada"
        assert menu.dessert == "Fruta"
        assert menu.allergens == ["gluten"]
        assert menu.created_at is not None

    def test_get_by_id_existing(self, db_session: Session, sample_student: StudentProfile):
        """Test retrieving an existing menu item by ID"""
        repo = MenuRepository(db_session)

        menu = repo.create(
            student_id=sample_student.id, date=date.today(), first_course="Pasta", second_course="Pescado"
        )

        retrieved = repo.get_by_id(menu.id)

        assert retrieved is not None
        assert retrieved.id == menu.id
        assert retrieved.first_course == "Pasta"

    def test_get_by_id_nonexistent(self, db_session: Session):
        """Test retrieving a non-existent menu item returns None"""
        repo = MenuRepository(db_session)

        result = repo.get_by_id(uuid4())

        assert result is None

    def test_get_by_student_id(self, db_session: Session, sample_student: StudentProfile):
        """Test retrieving all menu items for a student"""
        repo = MenuRepository(db_session)

        menu1 = repo.create(student_id=sample_student.id, date=date.today(), first_course="Sopa", second_course="Carne")
        menu2 = repo.create(
            student_id=sample_student.id,
            date=date.today() + timedelta(days=1),
            first_course="Arroz",
            second_course="Pollo",
        )

        menus = repo.get_by_student_id(sample_student.id)

        assert len(menus) == 2
        assert menu1 in menus
        assert menu2 in menus

    def test_get_by_student_id_date_range(self, db_session: Session, sample_student: StudentProfile):
        """Test retrieving menu items within a date range"""
        repo = MenuRepository(db_session)
        today = date.today()

        menu1 = repo.create(
            student_id=sample_student.id,
            date=today - timedelta(days=2),
            first_course="Past menu",
            second_course="Carne",
        )
        menu2 = repo.create(student_id=sample_student.id, date=today, first_course="Today menu", second_course="Pollo")
        menu3 = repo.create(
            student_id=sample_student.id,
            date=today + timedelta(days=2),
            first_course="Future menu",
            second_course="Pescado",
        )

        menus = repo.get_by_student_id(
            sample_student.id, start_date=today - timedelta(days=1), end_date=today + timedelta(days=1)
        )

        assert len(menus) == 1
        assert menus[0].id == menu2.id

    def test_get_by_date(self, db_session: Session, sample_student: StudentProfile):
        """Test retrieving a menu item by student and date"""
        repo = MenuRepository(db_session)
        menu_date = date.today()

        menu = repo.create(student_id=sample_student.id, date=menu_date, first_course="Lentejas", second_course="Pollo")

        retrieved = repo.get_by_date(sample_student.id, menu_date)

        assert retrieved is not None
        assert retrieved.id == menu.id
        assert retrieved.date == menu_date

    def test_get_by_date_not_found(self, db_session: Session, sample_student: StudentProfile):
        """Test retrieving menu by date when none exists"""
        repo = MenuRepository(db_session)

        result = repo.get_by_date(sample_student.id, date.today())

        assert result is None

    def test_update_menu_item(self, db_session: Session, sample_student: StudentProfile):
        """Test updating a menu item"""
        repo = MenuRepository(db_session)

        menu = repo.create(
            student_id=sample_student.id,
            date=date.today(),
            first_course="Original First",
            second_course="Original Second",
            dessert="Original Dessert",
        )

        updated = repo.update(
            menu_id=menu.id, first_course="Updated First", second_course="Updated Second", allergens=["lactose"]
        )

        assert updated.first_course == "Updated First"
        assert updated.second_course == "Updated Second"
        assert updated.dessert == "Original Dessert"  # Unchanged
        assert updated.allergens == ["lactose"]

    def test_update_partial(self, db_session: Session, sample_student: StudentProfile):
        """Test partial update of menu item"""
        repo = MenuRepository(db_session)

        menu = repo.create(
            student_id=sample_student.id,
            date=date.today(),
            first_course="Lentejas",
            second_course="Pollo",
            dessert="Fruta",
        )

        updated = repo.update(menu_id=menu.id, dessert="Yogur")

        assert updated.first_course == "Lentejas"  # Unchanged
        assert updated.second_course == "Pollo"  # Unchanged
        assert updated.dessert == "Yogur"  # Updated

    def test_delete_menu_item(self, db_session: Session, sample_student: StudentProfile):
        """Test soft deleting a menu item"""
        repo = MenuRepository(db_session)

        menu = repo.create(
            student_id=sample_student.id, date=date.today(), first_course="To Delete", second_course="Item"
        )

        result = repo.delete(menu.id)

        assert result is True

        # Menu should not be retrievable
        retrieved = repo.get_by_id(menu.id)
        assert retrieved is None

        # But should exist in DB with deleted_at set
        deleted_menu = db_session.query(MenuItem).filter(MenuItem.id == menu.id).first()
        assert deleted_menu is not None
        assert deleted_menu.deleted_at is not None

    def test_delete_nonexistent(self, db_session: Session):
        """Test deleting a non-existent menu item returns False"""
        repo = MenuRepository(db_session)

        result = repo.delete(uuid4())

        assert result is False

    def test_get_by_student_id_excludes_soft_deleted(self, db_session: Session, sample_student: StudentProfile):
        """Test that get_by_student_id doesn't return soft-deleted items"""
        repo = MenuRepository(db_session)

        menu1 = repo.create(
            student_id=sample_student.id, date=date.today(), first_course="Active", second_course="Item"
        )
        menu2 = repo.create(
            student_id=sample_student.id,
            date=date.today() + timedelta(days=1),
            first_course="Deleted",
            second_course="Item",
        )

        repo.delete(menu2.id)

        menus = repo.get_by_student_id(sample_student.id)

        assert len(menus) == 1
        assert menus[0].id == menu1.id

    def test_upsert_create_new(self, db_session: Session, sample_student: StudentProfile):
        """Test upsert creates new item when none exists for date"""
        repo = MenuRepository(db_session)
        menu_date = date.today()

        menu = repo.upsert(
            student_id=sample_student.id, date=menu_date, first_course="New First", second_course="New Second"
        )

        assert menu.id is not None
        assert menu.first_course == "New First"
        assert menu.second_course == "New Second"

    def test_upsert_update_existing(self, db_session: Session, sample_student: StudentProfile):
        """Test upsert updates existing item for same date"""
        repo = MenuRepository(db_session)
        menu_date = date.today()

        # Create initial menu
        original = repo.create(
            student_id=sample_student.id, date=menu_date, first_course="Original First", second_course="Original Second"
        )

        # Upsert with same date should update
        updated = repo.upsert(
            student_id=sample_student.id, date=menu_date, first_course="Updated First", second_course="Updated Second"
        )

        assert updated.id == original.id  # Same menu item
        assert updated.first_course == "Updated First"
        assert updated.second_course == "Updated Second"

        # Verify only one menu exists for this date
        menus = repo.get_by_student_id(sample_student.id)
        assert len(menus) == 1
