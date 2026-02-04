"""
Integration tests for Exam endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Skip tests when Docker/postgres isn't available
import docker

def _docker_available() -> bool:
    try:
        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False

pytestmark = pytest.mark.skipif(not _docker_available(), reason="Docker not available, skipping DB-backed integration tests")

from src.main import app
from src.infrastructure.database import get_db


@pytest.fixture
def client(db_session: Session):
    """Create test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestExamEndpoints:
    """Integration tests for exam API endpoints"""

    def register_and_login(self, client: TestClient, email: str = "exam@example.com"):
        """Helper to register and login a user"""
        # Register
        client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "SecurePass123!",
            "name": "Exam Tester"
        })
        # Login
        res = client.post("/api/v1/auth/login", json={
            "email": email,
            "password": "SecurePass123!"
        })
        token = res.json()["access_token"]
        return token

    def create_student(self, client: TestClient, token: str):
        """Helper to create a student"""
        payload = {
            "name": "Test Student",
            "school": "Colegio Test",
            "grade": "5º"
        }
        res = client.post("/api/v1/students", json=payload, headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 201
        return res.json()["id"]

    def test_create_exam(self, client: TestClient):
        """Test creating a new exam"""
        token = self.register_and_login(client)
        student_id = self.create_student(client, token)

        payload = {
            "subject": "Matemáticas",
            "date": "2026-03-15",
            "topic": "Ecuaciones de segundo grado",
            "notes": "Repasar ejercicios 1-10"
        }

        res = client.post(
            f"/api/v1/students/{student_id}/exams",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert res.status_code == 201
        data = res.json()
        assert data["student_id"] == student_id
        assert data["subject"] == "Matemáticas"
        assert data["date"] == "2026-03-15"
        assert data["topic"] == "Ecuaciones de segundo grado"
        assert data["notes"] == "Repasar ejercicios 1-10"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_exam_without_notes(self, client: TestClient):
        """Test creating an exam without notes"""
        token = self.register_and_login(client, email="exam2@example.com")
        student_id = self.create_student(client, token)

        payload = {
            "subject": "Lengua",
            "date": "2026-03-20",
            "topic": "Análisis sintáctico"
        }

        res = client.post(
            f"/api/v1/students/{student_id}/exams",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert res.status_code == 201
        data = res.json()
        assert data["notes"] is None

    def test_create_exam_unauthorized(self, client: TestClient):
        """Test creating exam without authentication"""
        payload = {
            "subject": "Historia",
            "date": "2026-04-01",
            "topic": "Revolución francesa"
        }

        res = client.post("/api/v1/students/00000000-0000-0000-0000-000000000000/exams", json=payload)
        assert res.status_code == 401

    def test_create_exam_for_another_users_student(self, client: TestClient):
        """Test creating exam for a student that doesn't belong to the user"""
        # User 1 creates a student
        token1 = self.register_and_login(client, email="user1@example.com")
        student_id = self.create_student(client, token1)

        # User 2 tries to create an exam for user 1's student
        token2 = self.register_and_login(client, email="user2@example.com")

        payload = {
            "subject": "Ciencias",
            "date": "2026-04-05",
            "topic": "Fotosíntesis"
        }

        res = client.post(
            f"/api/v1/students/{student_id}/exams",
            json=payload,
            headers={"Authorization": f"Bearer {token2}"}
        )

        assert res.status_code == 403

    def test_get_exams_for_student(self, client: TestClient):
        """Test retrieving all exams for a student"""
        token = self.register_and_login(client, email="getexams@example.com")
        student_id = self.create_student(client, token)

        # Create multiple exams
        exams = [
            {"subject": "Math", "date": "2026-03-10", "topic": "Algebra"},
            {"subject": "Science", "date": "2026-03-15", "topic": "Chemistry"},
            {"subject": "History", "date": "2026-03-20", "topic": "World War II"}
        ]

        for exam in exams:
            client.post(
                f"/api/v1/students/{student_id}/exams",
                json=exam,
                headers={"Authorization": f"Bearer {token}"}
            )

        # Get all exams
        res = client.get(
            f"/api/v1/students/{student_id}/exams",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert res.status_code == 200
        data = res.json()
        assert len(data) == 3
        # Should be ordered by date ascending
        assert data[0]["date"] == "2026-03-10"
        assert data[1]["date"] == "2026-03-15"
        assert data[2]["date"] == "2026-03-20"

    def test_get_exams_with_date_filters(self, client: TestClient):
        """Test retrieving exams with date range filters"""
        token = self.register_and_login(client, email="filters@example.com")
        student_id = self.create_student(client, token)

        # Create exams on different dates
        exams = [
            {"subject": "Math", "date": "2026-03-01", "topic": "Topic 1"},
            {"subject": "Science", "date": "2026-03-15", "topic": "Topic 2"},
            {"subject": "History", "date": "2026-03-30", "topic": "Topic 3"}
        ]

        for exam in exams:
            client.post(
                f"/api/v1/students/{student_id}/exams",
                json=exam,
                headers={"Authorization": f"Bearer {token}"}
            )

        # Test from_date filter
        res = client.get(
            f"/api/v1/students/{student_id}/exams?from_date=2026-03-10",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 2
        assert all(exam["date"] >= "2026-03-10" for exam in data)

        # Test to_date filter
        res = client.get(
            f"/api/v1/students/{student_id}/exams?to_date=2026-03-20",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 2
        assert all(exam["date"] <= "2026-03-20" for exam in data)

        # Test both filters
        res = client.get(
            f"/api/v1/students/{student_id}/exams?from_date=2026-03-10&to_date=2026-03-20",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["date"] == "2026-03-15"

    def test_get_exam_by_id(self, client: TestClient):
        """Test retrieving a specific exam by ID"""
        token = self.register_and_login(client, email="getone@example.com")
        student_id = self.create_student(client, token)

        # Create an exam
        create_res = client.post(
            f"/api/v1/students/{student_id}/exams",
            json={"subject": "Biology", "date": "2026-04-01", "topic": "Cell structure"},
            headers={"Authorization": f"Bearer {token}"}
        )
        exam_id = create_res.json()["id"]

        # Get the exam
        res = client.get(
            f"/api/v1/students/{student_id}/exams/{exam_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert res.status_code == 200
        data = res.json()
        assert data["id"] == exam_id
        assert data["subject"] == "Biology"

    def test_get_exam_not_found(self, client: TestClient):
        """Test retrieving non-existent exam"""
        token = self.register_and_login(client, email="notfound@example.com")
        student_id = self.create_student(client, token)

        res = client.get(
            f"/api/v1/students/{student_id}/exams/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert res.status_code == 404

    def test_update_exam(self, client: TestClient):
        """Test updating an exam"""
        token = self.register_and_login(client, email="update@example.com")
        student_id = self.create_student(client, token)

        # Create an exam
        create_res = client.post(
            f"/api/v1/students/{student_id}/exams",
            json={"subject": "Physics", "date": "2026-04-10", "topic": "Mechanics"},
            headers={"Authorization": f"Bearer {token}"}
        )
        exam_id = create_res.json()["id"]

        # Update the exam
        update_payload = {
            "subject": "Advanced Physics",
            "date": "2026-04-15",
            "topic": "Quantum Mechanics",
            "notes": "Study chapters 5-7"
        }

        res = client.put(
            f"/api/v1/students/{student_id}/exams/{exam_id}",
            json=update_payload,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert res.status_code == 200
        data = res.json()
        assert data["subject"] == "Advanced Physics"
        assert data["date"] == "2026-04-15"
        assert data["topic"] == "Quantum Mechanics"
        assert data["notes"] == "Study chapters 5-7"

    def test_update_exam_partial(self, client: TestClient):
        """Test partial update of an exam"""
        token = self.register_and_login(client, email="partialupdate@example.com")
        student_id = self.create_student(client, token)

        # Create an exam
        create_res = client.post(
            f"/api/v1/students/{student_id}/exams",
            json={"subject": "Chemistry", "date": "2026-04-20", "topic": "Periodic table"},
            headers={"Authorization": f"Bearer {token}"}
        )
        exam_id = create_res.json()["id"]

        # Update only the topic
        update_payload = {"topic": "Periodic table and chemical bonds"}

        res = client.put(
            f"/api/v1/students/{student_id}/exams/{exam_id}",
            json=update_payload,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert res.status_code == 200
        data = res.json()
        assert data["subject"] == "Chemistry"  # Unchanged
        assert data["date"] == "2026-04-20"  # Unchanged
        assert data["topic"] == "Periodic table and chemical bonds"  # Changed

    def test_delete_exam(self, client: TestClient):
        """Test deleting an exam (hard delete)"""
        token = self.register_and_login(client, email="delete@example.com")
        student_id = self.create_student(client, token)

        # Create an exam
        create_res = client.post(
            f"/api/v1/students/{student_id}/exams",
            json={"subject": "Geography", "date": "2026-05-01", "topic": "Continents"},
            headers={"Authorization": f"Bearer {token}"}
        )
        exam_id = create_res.json()["id"]

        # Delete the exam
        res = client.delete(
            f"/api/v1/students/{student_id}/exams/{exam_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert res.status_code == 204

        # Verify it's deleted (should return 404)
        get_res = client.get(
            f"/api/v1/students/{student_id}/exams/{exam_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_res.status_code == 404

    def test_delete_exam_not_found(self, client: TestClient):
        """Test deleting non-existent exam"""
        token = self.register_and_login(client, email="deletenotfound@example.com")
        student_id = self.create_student(client, token)

        res = client.delete(
            f"/api/v1/students/{student_id}/exams/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert res.status_code == 404

    def test_exams_isolated_by_student(self, client: TestClient):
        """Test that exams are properly isolated between students"""
        token = self.register_and_login(client, email="isolation@example.com")

        # Create two students
        student1_id = self.create_student(client, token)
        student2_payload = {
            "name": "Second Student",
            "school": "Another School",
            "grade": "6º"
        }
        res = client.post("/api/v1/students", json=student2_payload, headers={"Authorization": f"Bearer {token}"})
        student2_id = res.json()["id"]

        # Create exam for student 1
        client.post(
            f"/api/v1/students/{student1_id}/exams",
            json={"subject": "Math", "date": "2026-03-15", "topic": "Topic 1"},
            headers={"Authorization": f"Bearer {token}"}
        )

        # Create exam for student 2
        client.post(
            f"/api/v1/students/{student2_id}/exams",
            json={"subject": "Science", "date": "2026-03-15", "topic": "Topic 2"},
            headers={"Authorization": f"Bearer {token}"}
        )

        # Get exams for each student
        res1 = client.get(f"/api/v1/students/{student1_id}/exams", headers={"Authorization": f"Bearer {token}"})
        res2 = client.get(f"/api/v1/students/{student2_id}/exams", headers={"Authorization": f"Bearer {token}"})

        data1 = res1.json()
        data2 = res2.json()

        assert len(data1) == 1
        assert len(data2) == 1
        assert data1[0]["subject"] == "Math"
        assert data2[0]["subject"] == "Science"
