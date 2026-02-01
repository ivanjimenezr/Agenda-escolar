"""
Integration tests for Subject endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

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


class TestSubjectEndpoints:
    def register_and_login(self, client: TestClient, email: str = "subj@example.com"):
        # Register
        client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "SecurePass123!",
            "name": "Subject Tester"
        })
        # Login
        res = client.post("/api/v1/auth/login", json={
            "email": email,
            "password": "SecurePass123!"
        })
        token = res.json()["access_token"]
        return token

    def create_student(self, client: TestClient, token: str):
        payload = {
            "name": "Test Student",
            "school": "Colegio Test",
            "grade": "5º"
        }
        res = client.post("/api/v1/students", json=payload, headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 201
        return res.json()["id"]

    def test_create_subject_without_student_id_and_empty_teacher(self, client: TestClient):
        token = self.register_and_login(client)
        student_id = self.create_student(client, token)

        # Payload intentionally omits `student_id` and sets teacher to empty string
        payload = {
            "name": "futbol",
            "days": ["Lunes", "Domingo"],
            "time": "09:00",
            "teacher": "",
            "color": "#3b82f6",
            "type": "colegio"
        }

        res = client.post(f"/api/v1/students/{student_id}/subjects", json=payload, headers={"Authorization": f"Bearer {token}"})

        # Expect success (our previous fix allows omitting student_id in body and treats empty teacher correctly)
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["student_id"] == student_id
        # teacher may be empty string or null depending on how repository/response serialize it; accept both
        assert data.get("teacher") in (None, "")

    def test_conflict_and_replace_flow(self, client: TestClient):
        token = self.register_and_login(client, email="conflict@example.com")
        student_id = self.create_student(client, token)

        # Create initial subject at 09:00 on Lunes
        payload1 = {
            "name": "Matemáticas",
            "days": ["Lunes"],
            "time": "09:00",
            "teacher": "Ana",
            "color": "#ff0000",
            "type": "colegio"
        }
        res1 = client.post(f"/api/v1/students/{student_id}/subjects", json=payload1, headers={"Authorization": f"Bearer {token}"})
        assert res1.status_code == 201
        created1 = res1.json()

        # Try to create another subject that conflicts (same time and overlapping day)
        payload2 = {
            "name": "Fútbol",
            "days": ["Lunes", "Domingo"],
            "time": "09:00",
            "teacher": "",
            "color": "#3b82f6",
            "type": "extraescolar"
        }
        res2 = client.post(f"/api/v1/students/{student_id}/subjects", json=payload2, headers={"Authorization": f"Bearer {token}"})

        # Expect conflict response with details
        assert res2.status_code == 409, res2.text
        body = res2.json()
        assert "conflicts" in body["detail"]
        conflicts = body["detail"]["conflicts"]
        assert any(c["id"] == created1["id"] for c in conflicts)

        # Now replace existing by sending replace=true
        res3 = client.post(f"/api/v1/students/{student_id}/subjects?replace=true", json=payload2, headers={"Authorization": f"Bearer {token}"})
        assert res3.status_code == 201, res3.text
        created2 = res3.json()
        assert created2["name"] == "Fútbol"

        # Verify the original is soft-deleted by trying to GET it (should 404)
        res_get_old = client.get(f"/api/v1/students/{student_id}/subjects/{created1['id']}", headers={"Authorization": f"Bearer {token}"})
        assert res_get_old.status_code == 404

    def test_conflict_with_uppercase_days(self, client: TestClient):
        token = self.register_and_login(client, email="upper@example.com")
        student_id = self.create_student(client, token)

        payload1 = {
            "name": "Música",
            "days": ["Lunes"],
            "time": "10:00",
            "teacher": "Luis",
            "color": "#00ff00",
            "type": "colegio"
        }
        res1 = client.post(f"/api/v1/students/{student_id}/subjects", json=payload1, headers={"Authorization": f"Bearer {token}"})
        assert res1.status_code == 201

        # Use uppercase day names in payload to simulate frontend sending enum names
        payload2 = {
            "name": "Piano",
            "days": ["LUNES"],
            "time": "10:00",
            "teacher": "",
            "color": "#0000ff",
            "type": "extraescolar"
        }
        res2 = client.post(f"/api/v1/students/{student_id}/subjects", json=payload2, headers={"Authorization": f"Bearer {token}"})
        # Should still detect conflict (no server error)
        assert res2.status_code == 409, res2.text
        body = res2.json()
        assert "conflicts" in body["detail"]
        assert len(body["detail"]["conflicts"]) >= 1

