"""
Event Use Cases

Business logic for school event operations
"""

from datetime import date
from typing import List, Optional
from uuid import UUID

from src.application.schemas.event import (
    EventCreateRequest,
    EventUpdateRequest
)
from src.domain.models import SchoolEvent
from src.infrastructure.repositories.event_repository import EventRepository


class EventUseCases:
    """Use cases for school event management"""

    def __init__(self, event_repo: EventRepository):
        self.event_repo = event_repo

    def create_event(
        self,
        user_id: UUID,
        data: EventCreateRequest
    ) -> SchoolEvent:
        """Create a new school event for a user

        Args:
            user_id: ID of the user creating the event
            data: Event creation data

        Returns:
            Created SchoolEvent

        Raises:
            ValueError: If validation fails
        """
        return self.event_repo.create(
            user_id=user_id,
            date=data.date,
            name=data.name,
            event_type=data.type
        )

    def get_event_by_id(
        self,
        event_id: UUID,
        user_id: UUID
    ) -> SchoolEvent:
        """Get an event by ID

        Args:
            event_id: ID of the event
            user_id: ID of the requesting user

        Returns:
            SchoolEvent

        Raises:
            ValueError: If event not found
            PermissionError: If user doesn't own the event
        """
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise ValueError("Event not found")

        # Verify ownership
        if event.user_id != user_id:
            raise PermissionError("Access denied")

        return event

    def get_events_by_user(
        self,
        user_id: UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[SchoolEvent]:
        """Get all events for a user

        Args:
            user_id: ID of the user
            from_date: Optional filter - only events from this date onwards
            to_date: Optional filter - only events until this date

        Returns:
            List of SchoolEvent objects ordered by date
        """
        return self.event_repo.get_by_user_id(
            user_id=user_id,
            from_date=from_date,
            to_date=to_date
        )

    def update_event(
        self,
        event_id: UUID,
        user_id: UUID,
        data: EventUpdateRequest
    ) -> SchoolEvent:
        """Update an event

        Args:
            event_id: ID of the event
            user_id: ID of the requesting user
            data: Update data

        Returns:
            Updated SchoolEvent

        Raises:
            ValueError: If event not found
            PermissionError: If user doesn't own the event
        """
        # Get event and verify ownership
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise ValueError("Event not found")

        if event.user_id != user_id:
            raise PermissionError("Access denied")

        updated = self.event_repo.update(
            event_id=event_id,
            date=data.date,
            name=data.name,
            event_type=data.type
        )

        if not updated:
            raise ValueError("Event not found")

        return updated

    def delete_event(
        self,
        event_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete an event (hard delete)

        Args:
            event_id: ID of the event
            user_id: ID of the requesting user

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If event not found
            PermissionError: If user doesn't own the event
        """
        # Get event and verify ownership
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise ValueError("Event not found")

        if event.user_id != user_id:
            raise PermissionError("Access denied")

        result = self.event_repo.delete(event_id)

        if not result:
            raise ValueError("Event not found")

        return True
