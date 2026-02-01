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
