"""
Event API Endpoints

REST API routes for school event management
"""

from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.application.schemas.event import (
    EventCreateRequest,
    EventUpdateRequest,
    EventResponse
)
from src.application.use_cases.event_use_cases import EventUseCases
from src.domain.models import User
from src.infrastructure.api.dependencies.auth import get_current_user
from src.infrastructure.api.dependencies.database import get_db
from src.infrastructure.repositories.event_repository import EventRepository


router = APIRouter(prefix="/events", tags=["events"])


def get_event_use_cases(db: Session = Depends(get_db)) -> EventUseCases:
    """Dependency to get EventUseCases instance"""
    event_repo = EventRepository(db)
    return EventUseCases(event_repo)


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new school event"
)
def create_event(
    data: EventCreateRequest,
    current_user: User = Depends(get_current_user),
    use_cases: EventUseCases = Depends(get_event_use_cases)
):
    """
    Create a new school event for the current user.

    - **date**: Event date (YYYY-MM-DD format)
    - **name**: Event name (e.g., "Navidad", "Inicio de vacaciones")
    - **type**: Event type ("Festivo", "Lectivo", "Vacaciones")
    """
    try:
        event = use_cases.create_event(current_user.id, data)
        return EventResponse.model_validate(event)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=List[EventResponse],
    summary="Get all events for current user"
)
def get_user_events(
    from_date: Optional[date] = Query(None, description="Filter events from this date onwards"),
    to_date: Optional[date] = Query(None, description="Filter events until this date"),
    current_user: User = Depends(get_current_user),
    use_cases: EventUseCases = Depends(get_event_use_cases)
):
    """
    Get all events for the current user.

    Optionally filter by date range using from_date and to_date query parameters.
    Returns events ordered by date (ascending).
    """
    events = use_cases.get_events_by_user(
        user_id=current_user.id,
        from_date=from_date,
        to_date=to_date
    )
    return [EventResponse.model_validate(e) for e in events]


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    summary="Get a specific event"
)
def get_event(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    use_cases: EventUseCases = Depends(get_event_use_cases)
):
    """
    Get a specific event by ID.

    Requires ownership verification.
    """
    try:
        event = use_cases.get_event_by_id(event_id, current_user.id)
        return EventResponse.model_validate(event)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.put(
    "/{event_id}",
    response_model=EventResponse,
    summary="Update an event"
)
def update_event(
    event_id: UUID,
    data: EventUpdateRequest,
    current_user: User = Depends(get_current_user),
    use_cases: EventUseCases = Depends(get_event_use_cases)
):
    """
    Update an event.

    Only the owner can update the event.
    All fields are optional - only provided fields will be updated.
    """
    try:
        event = use_cases.update_event(event_id, current_user.id, data)
        return EventResponse.model_validate(event)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an event"
)
def delete_event(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    use_cases: EventUseCases = Depends(get_event_use_cases)
):
    """
    Delete an event (hard delete - permanent).

    Only the owner can delete the event.
    """
    try:
        use_cases.delete_event(event_id, current_user.id)
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
