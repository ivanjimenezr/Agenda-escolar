"""
Unit tests for User API routes
"""
import pytest
from fastapi import status
from datetime import datetime
from uuid import uuid4

from src.domain.models import User
from src.infrastructure.security import get_password_hash


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        id=uuid4(),
        email="test@example.com",
        name="Test User",
        hashed_password=get_password_hash("TestPassword123"),
        is_active=True,
        email_verified=False,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers for test user"""
    from src.infrastructure.security import create_access_token
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


def test_get_current_user_success(client, test_user, auth_headers):
    """Test getting current user information"""
    response = client.get("/api/v1/users/me", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name
    assert data["is_active"] == test_user.is_active
    assert "id" in data


def test_get_current_user_unauthorized(client):
    """Test getting current user without authentication"""
    response = client.get("/api/v1/users/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_user_name_success(client, test_user, auth_headers, db_session):
    """Test updating user name"""
    new_name = "Updated Name"
    response = client.put(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"name": new_name}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == new_name

    # Verify in database
    db_session.refresh(test_user)
    assert test_user.name == new_name


def test_update_user_email_success(client, test_user, auth_headers, db_session):
    """Test updating user email"""
    new_email = "newemail@example.com"
    response = client.put(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"email": new_email}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == new_email

    # Verify in database
    db_session.refresh(test_user)
    assert test_user.email == new_email


def test_update_user_email_already_exists(client, test_user, auth_headers, db_session):
    """Test updating email to one that already exists"""
    # Create another user with a different email
    other_user = User(
        id=uuid4(),
        email="other@example.com",
        name="Other User",
        hashed_password=get_password_hash("password"),
        is_active=True,
        email_verified=False,
        created_at=datetime.utcnow()
    )
    db_session.add(other_user)
    db_session.commit()

    # Try to update to the other user's email
    response = client.put(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"email": "other@example.com"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"].lower()


def test_update_user_password_success(client, test_user, auth_headers, db_session):
    """Test updating user password"""
    response = client.put(
        "/api/v1/users/me",
        headers=auth_headers,
        json={
            "current_password": "TestPassword123",
            "new_password": "NewPassword456"
        }
    )

    assert response.status_code == status.HTTP_200_OK

    # Verify password was changed
    from src.infrastructure.security import verify_password
    db_session.refresh(test_user)
    assert verify_password("NewPassword456", test_user.hashed_password)
    assert not verify_password("TestPassword123", test_user.hashed_password)


def test_update_user_password_wrong_current(client, test_user, auth_headers):
    """Test updating password with wrong current password"""
    response = client.put(
        "/api/v1/users/me",
        headers=auth_headers,
        json={
            "current_password": "WrongPassword",
            "new_password": "NewPassword456"
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "incorrect" in response.json()["detail"].lower()


def test_update_user_combined_fields(client, test_user, auth_headers, db_session):
    """Test updating multiple fields at once"""
    response = client.put(
        "/api/v1/users/me",
        headers=auth_headers,
        json={
            "name": "New Name",
            "email": "newemail@example.com",
            "current_password": "TestPassword123",
            "new_password": "NewPassword456"
        }
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "New Name"
    assert data["email"] == "newemail@example.com"

    # Verify in database
    from src.infrastructure.security import verify_password
    db_session.refresh(test_user)
    assert test_user.name == "New Name"
    assert test_user.email == "newemail@example.com"
    assert verify_password("NewPassword456", test_user.hashed_password)


def test_update_user_unauthorized(client):
    """Test updating user without authentication"""
    response = client.put(
        "/api/v1/users/me",
        json={"name": "New Name"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_user_success(client, test_user, auth_headers, db_session):
    """Test deleting user account (soft delete)"""
    user_id = test_user.id

    response = client.delete("/api/v1/users/me", headers=auth_headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify soft delete in database
    db_session.refresh(test_user)
    assert test_user.deleted_at is not None


def test_delete_user_unauthorized(client):
    """Test deleting user without authentication"""
    response = client.delete("/api/v1/users/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_user_partial_fields(client, test_user, auth_headers, db_session):
    """Test updating only some fields (all fields are optional)"""
    original_email = test_user.email

    response = client.put(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"name": "Only Name Changed"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Only Name Changed"
    assert data["email"] == original_email  # Email unchanged
