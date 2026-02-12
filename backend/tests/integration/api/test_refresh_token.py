"""
Integration tests for refresh token rotation.

Tests cover:
- Login returns a refresh_token alongside access_token
- POST /auth/refresh issues new tokens and invalidates the old refresh token
- A revoked (already-used) refresh token triggers reuse detection (HTTP 401)
- An invalid/random refresh token is rejected (HTTP 401)
- POST /auth/logout revokes the refresh token (HTTP 200)
- After logout, the refresh token can no longer be used (HTTP 401)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.infrastructure.api.rate_limit import limiter
from src.infrastructure.database import get_db
from src.main import app

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

REGISTER_PAYLOAD = {
    "email": "refresh_test@example.com",
    "password": "SecurePass123!",
    "name": "Refresh Test User",
}


@pytest.fixture
def client(db_session: Session):
    """Create test client with in-memory DB override and reset rate limiter."""
    limiter._limiter.storage.reset()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client: TestClient):
    """Register a user and return its credentials."""
    client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    return REGISTER_PAYLOAD


@pytest.fixture
def tokens(client: TestClient, registered_user):
    """Login and return the full token response dict."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    assert response.status_code == 200
    return response.json()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestLoginReturnsRefreshToken:
    """Login must now return both access_token and refresh_token."""

    def test_login_returns_refresh_token(self, client: TestClient, registered_user):
        """POST /auth/login response includes refresh_token field."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": registered_user["email"], "password": registered_user["password"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        # The refresh token is an opaque string (URL-safe base64, ~43 chars)
        assert isinstance(data["refresh_token"], str)
        assert len(data["refresh_token"]) > 20


class TestRefreshEndpoint:
    """POST /auth/refresh rotates the refresh token."""

    def test_refresh_returns_new_tokens(self, client: TestClient, tokens):
        """Valid refresh token produces a new access_token and refresh_token."""
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        # The new refresh token is always different (cryptographically random)
        assert data["refresh_token"] != tokens["refresh_token"]
        # The new access token contains valid user data
        assert "user" in data
        assert data["user"]["email"] == tokens["user"]["email"]

    def test_refresh_new_access_token_is_usable(self, client: TestClient, tokens):
        """The new access token can authenticate requests."""
        refresh_response = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        new_access_token = refresh_response.json()["access_token"]

        me_response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {new_access_token}"},
        )
        assert me_response.status_code == 200

    def test_refresh_invalidates_old_refresh_token(self, client: TestClient, tokens):
        """After rotation the old refresh token must be rejected (one-time use)."""
        old_refresh = tokens["refresh_token"]

        # Use the token once (valid)
        client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})

        # Attempt to reuse the old token
        reuse_response = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
        assert reuse_response.status_code == 401

    def test_refresh_reuse_detection_revokes_all_sessions(self, client: TestClient, tokens):
        """
        Presenting a revoked refresh token (reuse attack) must invalidate
        ALL sessions: even the new refresh token from the legitimate rotation
        must no longer work.
        """
        old_refresh = tokens["refresh_token"]

        # Legitimate rotation: produces a new refresh token
        rotation_response = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
        new_refresh = rotation_response.json()["refresh_token"]

        # Attacker replays the OLD (now revoked) token → triggers reuse detection
        client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})

        # The legitimate new token must also be revoked now
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": new_refresh})
        assert response.status_code == 401

    def test_refresh_invalid_token_rejected(self, client: TestClient):
        """A random/unknown refresh token must be rejected with 401."""
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": "this-is-not-a-valid-token"})
        assert response.status_code == 401

    def test_refresh_chain_works(self, client: TestClient, tokens):
        """Multiple sequential rotations must all succeed (chain of valid uses)."""
        current_refresh = tokens["refresh_token"]

        for _ in range(3):
            response = client.post("/api/v1/auth/refresh", json={"refresh_token": current_refresh})
            assert response.status_code == 200
            current_refresh = response.json()["refresh_token"]


class TestLogoutEndpoint:
    """POST /auth/logout revokes the refresh token."""

    def test_logout_success(self, client: TestClient, tokens):
        """Valid refresh token is accepted and revoked."""
        response = client.post("/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]})

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_after_logout_refresh_token_is_invalid(self, client: TestClient, tokens):
        """After logout, the refresh token can no longer be rotated."""
        refresh_token = tokens["refresh_token"]

        # Logout
        client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})

        # Try to refresh → must fail
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == 401

    def test_logout_unknown_token_returns_400(self, client: TestClient):
        """Attempting to logout with an unknown token returns 400."""
        response = client.post("/api/v1/auth/logout", json={"refresh_token": "completely-unknown-token"})
        assert response.status_code == 400
