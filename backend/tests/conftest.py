"""
Pytest configuration and fixtures for testing.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typing import Generator

from src.infrastructure.database import Base
from src.domain import models  # Import all models to register them


# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator:
    """
    Create a fresh database session for each test.
    Creates all tables before the test and drops them after.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create a new session
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop all tables after the test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "password": "SecurePass123!",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS.i7oWu2"  # bcrypt hash of "SecurePass123!"
    }


# TestClient fixture used by API route unit tests. It overrides the real DB
# dependency to use the in-memory testing session created in this file.
from fastapi.testclient import TestClient
from src.main import app
from src.infrastructure.api.dependencies.database import get_db as real_get_db

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[real_get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.pop(real_get_db, None)
