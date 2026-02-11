"""
Integration tests for User API endpoints.
Following TDD principles - write tests first, then implement.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.infrastructure.api.rate_limit import limiter
from src.infrastructure.database import get_db
from src.main import app


@pytest.fixture
def client(db_session: Session):
    """Create test client with database override."""
    # Resetear rate limiter entre tests para evitar falsos 429
    limiter._limiter.storage.reset()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestUserEndpoints:
    """Integration tests for user API endpoints."""

    def test_register_user_success(self, client: TestClient):
        """Test POST /api/v1/auth/register - successful registration."""
        # Arrange
        payload = {"email": "test@example.com", "password": "SecurePass123!", "name": "Test User"}

        # Act
        response = client.post("/api/v1/auth/register", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == payload["email"]
        assert data["name"] == payload["name"]
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data
        assert data["is_active"] is True
        assert data["email_verified"] is False

    def test_register_user_duplicate_email(self, client: TestClient):
        """Test POST /api/v1/auth/register - duplicate email fails."""
        # Arrange
        payload = {"email": "duplicate@example.com", "password": "SecurePass123!", "name": "First User"}
        client.post("/api/v1/auth/register", json=payload)

        # Act - Try to register again with same email
        payload2 = {"email": "duplicate@example.com", "password": "AnotherPass456!", "name": "Second User"}
        response = client.post("/api/v1/auth/register", json=payload2)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_register_user_invalid_email(self, client: TestClient):
        """Test POST /api/v1/auth/register - invalid email format."""
        # Arrange
        payload = {"email": "not-an-email", "password": "SecurePass123!", "name": "Test User"}

        # Act
        response = client.post("/api/v1/auth/register", json=payload)

        # Assert
        assert response.status_code == 422  # Validation error

    def test_register_user_short_password(self, client: TestClient):
        """Test POST /api/v1/auth/register - password too short."""
        # Arrange
        payload = {"email": "test@example.com", "password": "short", "name": "Test User"}  # Less than 8 characters

        # Act
        response = client.post("/api/v1/auth/register", json=payload)

        # Assert
        assert response.status_code == 422  # Validation error

    def test_login_user_success(self, client: TestClient):
        """Test POST /api/v1/auth/login - successful login."""
        # Arrange - Register user first
        register_payload = {"email": "login@example.com", "password": "SecurePass123!", "name": "Login User"}
        client.post("/api/v1/auth/register", json=register_payload)

        # Act - Login
        login_payload = {"email": "login@example.com", "password": "SecurePass123!"}
        response = client.post("/api/v1/auth/login", json=login_payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == login_payload["email"]

    def test_login_user_wrong_password(self, client: TestClient):
        """Test POST /api/v1/auth/login - wrong password fails."""
        # Arrange - Register user
        register_payload = {"email": "user@example.com", "password": "CorrectPass123!", "name": "User"}
        client.post("/api/v1/auth/register", json=register_payload)

        # Act - Login with wrong password
        login_payload = {"email": "user@example.com", "password": "WrongPass456!"}
        response = client.post("/api/v1/auth/login", json=login_payload)

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_login_user_non_existing_email(self, client: TestClient):
        """Test POST /api/v1/auth/login - non-existing email fails."""
        # Arrange
        login_payload = {"email": "nonexistent@example.com", "password": "SomePass123!"}

        # Act
        response = client.post("/api/v1/auth/login", json=login_payload)

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_get_current_user_success(self, client: TestClient):
        """Test GET /api/v1/users/me - get current authenticated user."""
        # Arrange - Register and login
        register_payload = {"email": "current@example.com", "password": "SecurePass123!", "name": "Current User"}
        client.post("/api/v1/auth/register", json=register_payload)

        login_response = client.post(
            "/api/v1/auth/login", json={"email": "current@example.com", "password": "SecurePass123!"}
        )
        token = login_response.json()["access_token"]

        # Act - Get current user
        response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "current@example.com"
        assert data["name"] == "Current User"

    def test_get_current_user_without_token(self, client: TestClient):
        """Test GET /api/v1/users/me - without token fails."""
        # Act
        response = client.get("/api/v1/users/me")

        # Assert
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test GET /api/v1/users/me - with invalid token fails."""
        # Act
        response = client.get("/api/v1/users/me", headers={"Authorization": "Bearer invalid_token_here"})

        # Assert
        assert response.status_code == 401

    def test_login_rate_limit(self, client: TestClient):
        """Test POST /api/v1/auth/login - rate limited after 5 requests per minute."""
        # Arrange
        login_payload = {"email": "ratelimit@example.com", "password": "SomePass123!"}

        # Act - Enviar 6 peticiones consecutivas (limite: 5/minuto)
        responses = []
        for _ in range(6):
            resp = client.post("/api/v1/auth/login", json=login_payload)
            responses.append(resp)

        # Assert - Las primeras 5 deben pasar (401 porque el usuario no existe, pero NO 429)
        for resp in responses[:5]:
            assert resp.status_code != 429

        # La 6a peticion debe ser rechazada con 429 Too Many Requests
        assert responses[5].status_code == 429
