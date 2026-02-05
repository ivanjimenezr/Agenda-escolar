"""
Event Repository

Data access layer for SchoolEvent entity
"""

from datetime import date, datetime, time, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.domain.models import SchoolEvent


class EventRepository:
    """Repository for school event data access"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: UUID,
        date: date,
        name: str,
        event_type: str,
        time: Optional[time] = None,
        description: Optional[str] = None,
    ) -> SchoolEvent:
        """Create a new school event

        Args:
            user_id: UUID of the user
            date: Event date
            name: Event name
            event_type: Event type (Festivo, Lectivo, Vacaciones)
            time: Optional event time
            description: Optional event description

        Returns:
            Created SchoolEvent

        Raises:
            ValueError: If database error occurs
        """
        event = SchoolEvent(
            user_id=user_id, date=date, name=name, type=event_type, time=time, description=description
        )

        self.db.add(event)
        try:
            self.db.commit()
            self.db.refresh(event)
            return event
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to create event: {str(e)}")

    def get_by_id(self, event_id: UUID) -> Optional[SchoolEvent]:
        """Get event by ID"""
        return self.db.query(SchoolEvent).filter(SchoolEvent.id == event_id).first()

    def get_by_user_id(
        self, user_id: UUID, from_date: Optional[date] = None, to_date: Optional[date] = None
    ) -> List[SchoolEvent]:
        """Get all events for a user

        Args:
            user_id: UUID of the user
            from_date: Optional filter - only events from this date onwards
            to_date: Optional filter - only events until this date

        Returns:
            List of events ordered by date ascending
        """
        query = self.db.query(SchoolEvent).filter(SchoolEvent.user_id == user_id)

        if from_date:
            query = query.filter(SchoolEvent.date >= from_date)
        if to_date:
            query = query.filter(SchoolEvent.date <= to_date)

        return query.order_by(SchoolEvent.date.asc()).all()

    def update(
        self,
        event_id: UUID,
        date: Optional[date] = ...,
        name: Optional[str] = ...,
        event_type: Optional[str] = ...,
        time: Optional[time] = ...,
        description: Optional[str] = ...,
    ) -> Optional[SchoolEvent]:
        """Update event

        Args:
            event_id: UUID of the event
            date: Optional new date (Ellipsis means not provided)
            name: Optional new name (Ellipsis means not provided)
            event_type: Optional new type (Ellipsis means not provided)
            time: Optional new time (Ellipsis means not provided, None means clear it)
            description: Optional new description (Ellipsis means not provided, None means clear it)

        Returns:
            Updated SchoolEvent or None if not found
        """
        event = self.get_by_id(event_id)
        if not event:
            return None

        if date is not ...:
            event.date = date
        if name is not ...:
            event.name = name
        if event_type is not ...:
            event.type = event_type
        if time is not ...:
            event.time = time
        if description is not ...:
            event.description = description

        event.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(event)
        return event

    def delete(self, event_id: UUID) -> bool:
        """Hard delete an event (permanent deletion)

        Args:
            event_id: UUID of the event to delete

        Returns:
            True if deleted, False if not found
        """
        event = self.get_by_id(event_id)
        if not event:
            return False

        self.db.delete(event)
        self.db.commit()
        return True
