"""
Integration tests for Menu API endpoints

These tests specifically test Pydantic serialization of SQLAlchemy models
to catch RecursionError issues before deployment.
"""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from src.application.schemas.menu import MenuItemResponse
from src.domain.models import MenuItem, StudentProfile, User
from src.main import app


@pytest.fixture
def auth_headers(client: TestClient, db_session):
    """Create a user and return authentication headers"""
    from src.infrastructure.security.jwt import create_access_token
    from src.infrastructure.security.password import hash_password

    # Create user
    user = User(email="testmenu@example.com", name="Test Menu User", password_hash=hash_password("testpassword123"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Create access token
    token = create_access_token({"sub": str(user.id)})

    return {"Authorization": f"Bearer {token}"}, user


@pytest.fixture
def sample_student(db_session, auth_headers):
    """Create a sample student profile"""
    headers, user = auth_headers

    student = StudentProfile(
        user_id=user.id,
        name="Test Student Menu",
        school="Test School",
        grade="5th Grade",
        allergies=["gluten", "lactose"],
        excluded_foods=["nuts"],
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)

    return student


class TestMenuEndpointsSerialization:
    """Test suite specifically for Pydantic serialization issues"""

    def test_create_menu_and_serialize(self, client: TestClient, auth_headers, sample_student, db_session):
        """Test creating a menu item and serializing the response"""
        headers, user = auth_headers
        menu_date = date.today().isoformat()

        payload = {
            "student_id": str(sample_student.id),
            "date": menu_date,
            "first_course": "Lentejas con chorizo",
            "second_course": "Pollo asado con patatas",
            "side_dish": "Ensalada mixta",
            "dessert": "Fruta de temporada",
            "allergens": ["gluten"],
        }

        response = client.post("/menus", json=payload, headers=headers)

        assert response.status_code == 201
        data = response.json()

        # Verify all fields are present
        assert "id" in data
        assert data["student_id"] == str(sample_student.id)
        assert data["first_course"] == "Lentejas con chorizo"
        assert data["second_course"] == "Pollo asado con patatas"
        assert data["allergens"] == ["gluten"]

        # This line will trigger RecursionError if relationships are loaded
        assert "student" not in data  # Should not include relationship

    def test_get_student_menus_serialization(self, client: TestClient, auth_headers, sample_student, db_session):
        """Test getting multiple menus - this is where RecursionError typically occurs"""
        headers, user = auth_headers

        # Create multiple menu items
        from src.infrastructure.repositories.menu_repository import MenuRepository

        repo = MenuRepository(db_session)

        menu1 = repo.create(
            student_id=sample_student.id,
            date=date.today(),
            first_course="Sopa de verduras",
            second_course="Merluza al horno",
            allergens=[],
        )

        menu2 = repo.create(
            student_id=sample_student.id,
            date=date.today() + timedelta(days=1),
            first_course="Arroz con tomate",
            second_course="Filete de ternera",
            allergens=["gluten"],
        )

        menu3 = repo.create(
            student_id=sample_student.id,
            date=date.today() + timedelta(days=2),
            first_course="Pasta carbonara",
            second_course="Ensalada césar",
            allergens=["gluten", "lactose", "egg"],
        )

        # THIS IS THE CRITICAL TEST - Getting multiple menus
        response = client.get(f"/menus/student/{sample_student.id}", headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 3

        # Verify each menu item is properly serialized
        for menu_item in data:
            assert "id" in menu_item
            assert "student_id" in menu_item
            assert "first_course" in menu_item
            assert "second_course" in menu_item
            assert "allergens" in menu_item
            # Should NOT include relationship fields
            assert "student" not in menu_item

    def test_pydantic_model_validate_directly(self, db_session, sample_student):
        """Test Pydantic model_validate directly with SQLAlchemy model"""
        from src.infrastructure.repositories.menu_repository import MenuRepository

        repo = MenuRepository(db_session)

        menu = repo.create(
            student_id=sample_student.id,
            date=date.today(),
            first_course="Test First",
            second_course="Test Second",
            allergens=["test"],
        )

        # This is what happens in the endpoint - THIS SHOULD NOT CAUSE RecursionError
        try:
            response_model = MenuItemResponse.model_validate(menu)
            assert response_model.id == menu.id
            assert response_model.first_course == "Test First"
            assert response_model.student_id == sample_student.id
        except RecursionError as e:
            pytest.fail(f"RecursionError occurred during Pydantic serialization: {e}")

    def test_menu_with_date_range_filter(self, client: TestClient, auth_headers, sample_student, db_session):
        """Test getting menus with date range filters"""
        headers, user = auth_headers
        today = date.today()

        from src.infrastructure.repositories.menu_repository import MenuRepository

        repo = MenuRepository(db_session)

        # Create menus across different dates
        for i in range(5):
            repo.create(
                student_id=sample_student.id,
                date=today + timedelta(days=i),
                first_course=f"Course {i}",
                second_course=f"Second {i}",
                allergens=[],
            )

        # Get with date range
        start_date = (today + timedelta(days=1)).isoformat()
        end_date = (today + timedelta(days=3)).isoformat()

        response = client.get(
            f"/menus/student/{sample_student.id}?start_date={start_date}&end_date={end_date}", headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 3  # Days 1, 2, 3

        # Verify serialization worked
        for item in data:
            assert "id" in item
            assert "student" not in item

    def test_get_single_menu_by_id(self, client: TestClient, auth_headers, sample_student, db_session):
        """Test getting a single menu by ID"""
        headers, user = auth_headers

        from src.infrastructure.repositories.menu_repository import MenuRepository

        repo = MenuRepository(db_session)

        menu = repo.create(
            student_id=sample_student.id,
            date=date.today(),
            first_course="Single Menu Test",
            second_course="Test Second",
            allergens=["gluten"],
        )

        response = client.get(f"/menus/{menu.id}", headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(menu.id)
        assert data["first_course"] == "Single Menu Test"
        assert "student" not in data

    def test_update_menu_serialization(self, client: TestClient, auth_headers, sample_student, db_session):
        """Test updating a menu and serializing response"""
        headers, user = auth_headers

        from src.infrastructure.repositories.menu_repository import MenuRepository

        repo = MenuRepository(db_session)

        menu = repo.create(
            student_id=sample_student.id,
            date=date.today(),
            first_course="Original",
            second_course="Original Second",
            allergens=[],
        )

        update_payload = {"first_course": "Updated First Course", "allergens": ["updated", "allergen"]}

        response = client.put(f"/menus/{menu.id}", json=update_payload, headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert data["first_course"] == "Updated First Course"
        assert data["allergens"] == ["updated", "allergen"]
        assert "student" not in data

    def test_upsert_menu_serialization(self, client: TestClient, auth_headers, sample_student, db_session):
        """Test upsert endpoint serialization"""
        headers, user = auth_headers
        menu_date = date.today().isoformat()

        payload = {
            "student_id": str(sample_student.id),
            "date": menu_date,
            "first_course": "Upsert First",
            "second_course": "Upsert Second",
            "allergens": [],
        }

        # First upsert (create)
        response = client.put("/menus/upsert", json=payload, headers=headers)
        assert response.status_code == 200
        first_data = response.json()

        # Second upsert (update)
        payload["first_course"] = "Updated Upsert"
        response = client.put("/menus/upsert", json=payload, headers=headers)
        assert response.status_code == 200
        second_data = response.json()

        assert first_data["id"] == second_data["id"]  # Same ID
        assert second_data["first_course"] == "Updated Upsert"
        assert "student" not in second_data

    def test_multiple_students_no_recursion(self, client: TestClient, auth_headers, db_session):
        """Test with multiple students to ensure no cross-contamination"""
        headers, user = auth_headers

        # Create multiple students
        student1 = StudentProfile(user_id=user.id, name="Student 1", school="School 1", grade="5th")
        student2 = StudentProfile(user_id=user.id, name="Student 2", school="School 2", grade="6th")
        db_session.add_all([student1, student2])
        db_session.commit()
        db_session.refresh(student1)
        db_session.refresh(student2)

        from src.infrastructure.repositories.menu_repository import MenuRepository

        repo = MenuRepository(db_session)

        # Create menus for each student
        for student in [student1, student2]:
            for i in range(3):
                repo.create(
                    student_id=student.id,
                    date=date.today() + timedelta(days=i),
                    first_course=f"Course {i}",
                    second_course=f"Second {i}",
                    allergens=[],
                )

        # Get menus for student1
        response1 = client.get(f"/menus/student/{student1.id}", headers=headers)
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1) == 3

        # Get menus for student2
        response2 = client.get(f"/menus/student/{student2.id}", headers=headers)
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) == 3

        # Verify no recursion errors occurred
        for item in data1 + data2:
            assert "student" not in item
