"""
Unit tests for EventRepository
"""
import pytest
from datetime import date
from uuid import uuid4

from src.domain.models import SchoolEvent, User
from src.infrastructure.repositories.event_repository import EventRepository


@pytest.fixture
def event_repo(db_session):
    """Create EventRepository instance with test database session."""
    return EventRepository(db_session)


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(
        id=uuid4(),
        email="event_test@example.com",
        name="Event Test User",
        password_hash="dummy_hash",
        is_active=True,
        email_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestEventRepository:
    """Test suite for EventRepository"""

    def test_create_event(self, event_repo, sample_user):
        """Test creating a new event"""
        event = event_repo.create(
            user_id=sample_user.id,
            date=date(2026, 12, 25),
            name="Navidad",
            event_type="Festivo"
        )

        assert event.id is not None
        assert event.user_id == sample_user.id
        assert event.date == date(2026, 12, 25)
        assert event.name == "Navidad"
        assert event.type == "Festivo"
        assert event.created_at is not None
        assert event.updated_at is not None

    def test_create_event_lectivo(self, event_repo, sample_user):
        """Test creating a lectivo event"""
        event = event_repo.create(
            user_id=sample_user.id,
            date=date(2026, 9, 1),
            name="Inicio de curso",
            event_type="Lectivo"
        )

        assert event.id is not None
        assert event.type == "Lectivo"

    def test_get_by_id(self, event_repo, sample_user):
        """Test retrieving an event by ID"""
        created = event_repo.create(
            user_id=sample_user.id,
            date=date(2026, 1, 1),
            name="Año Nuevo",
            event_type="Festivo"
        )

        retrieved = event_repo.get_by_id(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Año Nuevo"

    def test_get_by_id_not_found(self, event_repo):
        """Test retrieving a non-existent event"""
        result = event_repo.get_by_id(uuid4())
        assert result is None

    def test_get_by_user_id(self, event_repo, sample_user):
        """Test retrieving all events for a user"""
        # Create multiple events
        event_repo.create(
            user_id=sample_user.id,
            date=date(2026, 12, 25),
            name="Navidad",
            event_type="Festivo"
        )
        event_repo.create(
            user_id=sample_user.id,
            date=date(2026, 1, 1),
            name="Año Nuevo",
            event_type="Festivo"
        )
        event_repo.create(
            user_id=sample_user.id,
            date=date(2026, 7, 1),
            name="Vacaciones de verano",
            event_type="Vacaciones"
        )

        events = event_repo.get_by_user_id(sample_user.id)

        assert len(events) == 3
        # Should be ordered by date ascending
        assert events[0].date == date(2026, 1, 1)
        assert events[1].date == date(2026, 7, 1)
        assert events[2].date == date(2026, 12, 25)

    def test_get_by_user_id_with_date_filters(self, event_repo, sample_user):
        """Test retrieving events with date range filters"""
        # Create events on different dates
        event_repo.create(
            user_id=sample_user.id,
            date=date(2026, 1, 1),
            name="Event 1",
            event_type="Festivo"
        )
        event_repo.create(
            user_id=sample_user.id,
            date=date(2026, 6, 15),
            name="Event 2",
            event_type="Lectivo"
        )
        event_repo.create(
            user_id=sample_user.id,
            date=date(2026, 12, 31),
            name="Event 3",
            event_type="Festivo"
        )

        # Test from_date filter
        events = event_repo.get_by_user_id(
            sample_user.id,
            from_date=date(2026, 6, 1)
        )
        assert len(events) == 2
        assert all(e.date >= date(2026, 6, 1) for e in events)

        # Test to_date filter
        events = event_repo.get_by_user_id(
            sample_user.id,
            to_date=date(2026, 6, 30)
        )
        assert len(events) == 2
        assert all(e.date <= date(2026, 6, 30) for e in events)

        # Test both filters
        events = event_repo.get_by_user_id(
            sample_user.id,
            from_date=date(2026, 6, 1),
            to_date=date(2026, 6, 30)
        )
        assert len(events) == 1
        assert events[0].date == date(2026, 6, 15)

    def test_update_event(self, event_repo, sample_user):
        """Test updating an event"""
        event = event_repo.create(
            user_id=sample_user.id,
            date=date(2026, 10, 12),
            name="Día de la Hispanidad",
            event_type="Festivo"
        )

        original_updated_at = event.updated_at

        # Update the event
        updated = event_repo.update(
            event_id=event.id,
            date=date(2026, 10, 12),
            name="Fiesta Nacional de España",
            event_type="Festivo"
        )

        assert updated is not None
        assert updated.name == "Fiesta Nacional de España"
        assert updated.updated_at > original_updated_at

    def test_update_partial(self, event_repo, sample_user):
        """Test partial update of an event"""
        event = event_repo.create(
            user_id=sample_user.id,
            date=date(2026, 3, 19),
            name="San José",
            event_type="Festivo"
        )

        # Only update the name
        updated = event_repo.update(
            event_id=event.id,
            name="San José (Fallas)"
        )

        assert updated is not None
        assert updated.date == date(2026, 3, 19)  # Unchanged
        assert updated.type == "Festivo"  # Unchanged
        assert updated.name == "San José (Fallas)"  # Changed

    def test_update_not_found(self, event_repo):
        """Test updating a non-existent event"""
        result = event_repo.update(
            event_id=uuid4(),
            name="New Name"
        )
        assert result is None

    def test_hard_delete(self, event_repo, sample_user):
        """Test hard delete (permanent deletion)"""
        event = event_repo.create(
            user_id=sample_user.id,
            date=date(2026, 4, 1),
            name="Día de los Inocentes",
            event_type="Festivo"
        )

        event_id = event.id

        # Delete the event
        result = event_repo.delete(event_id)
        assert result is True

        # Verify it's permanently deleted
        deleted_event = event_repo.get_by_id(event_id)
        assert deleted_event is None

    def test_delete_not_found(self, event_repo):
        """Test deleting a non-existent event"""
        result = event_repo.delete(uuid4())
        assert result is False

    def test_events_isolated_by_user(self, event_repo, db_session):
        """Test that events are properly isolated by user"""
        # Create two users
        user1 = User(
            id=uuid4(),
            email="user1@example.com",
            name="User 1",
            password_hash="hash1",
            is_active=True,
            email_verified=True
        )
        user2 = User(
            id=uuid4(),
            email="user2@example.com",
            name="User 2",
            password_hash="hash2",
            is_active=True,
            email_verified=True
        )
        db_session.add_all([user1, user2])
        db_session.commit()

        # Create events for each user
        event_repo.create(
            user_id=user1.id,
            date=date(2026, 1, 1),
            name="User 1 Event",
            event_type="Festivo"
        )
        event_repo.create(
            user_id=user2.id,
            date=date(2026, 1, 1),
            name="User 2 Event",
            event_type="Festivo"
        )

        # Verify isolation
        user1_events = event_repo.get_by_user_id(user1.id)
        user2_events = event_repo.get_by_user_id(user2.id)

        assert len(user1_events) == 1
        assert len(user2_events) == 1
        assert user1_events[0].name == "User 1 Event"
        assert user2_events[0].name == "User 2 Event"
