"""
Subject API Endpoints

REST API routes for subject management
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.application.schemas.subject import (
    SubjectCreateRequest,
    SubjectUpdateRequest,
    SubjectResponse
)
from src.application.use_cases.subject_use_cases import SubjectUseCases
from src.domain.models import User
from src.infrastructure.api.dependencies.auth import get_current_user
from src.infrastructure.api.dependencies.database import get_db
from src.infrastructure.repositories.subject_repository import SubjectRepository
from src.infrastructure.repositories.student_repository import StudentRepository


router = APIRouter(prefix="/students/{student_id}/subjects", tags=["subjects"])


def get_subject_use_cases(db: Session = Depends(get_db)) -> SubjectUseCases:
    """Dependency to get SubjectUseCases instance"""
    subject_repo = SubjectRepository(db)
    student_repo = StudentRepository(db)
    return SubjectUseCases(subject_repo, student_repo)


@router.post(
    "",
    response_model=SubjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new subject"
)
def create_subject(
    student_id: UUID,
    data: SubjectCreateRequest,
    replace: bool = False,
    current_user: User = Depends(get_current_user),
    use_cases: SubjectUseCases = Depends(get_subject_use_cases)
):
    """
    Create a new subject for a student.

    - **student_id**: UUID of the student (from path)
    - **name**: Subject name (e.g., "Matemáticas", "Fútbol")
    - **days**: List of weekdays (e.g., ["Lunes", "Miércoles", "Viernes"])
    - **time**: Time of the class (e.g., "09:00:00")
    - **teacher**: Teacher name
    - **color**: Hex color code (e.g., "#FF5733")
    - **type**: Subject type ("colegio" or "extraescolar")
    """
    # If student_id missing in body, fill it from the path; otherwise ensure they match
    if getattr(data, "student_id", None) is None:
        # create a copy of the request data with the student_id filled
        data = data.model_copy(update={"student_id": student_id})
    elif data.student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student ID in path must match student_id in request body"
        )

    try:
        subject = use_cases.create_subject(current_user.id, data, replace=replace)
        return SubjectResponse.model_validate(subject)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        # Handle conflict specially
        from src.application.exceptions import ConflictError
        if isinstance(e, ConflictError):
            # Build a conflicts summary
            conflicts = []
            for c in e.conflicts:
                conflicts.append({
                    "id": str(c.id),
                    "name": c.name,
                    "days": c.days,
                    "time": c.time.strftime("%H:%M") if c.time else None
                })
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": "Conflicting subject(s) exist at the same time", "conflicts": conflicts}
            )
        # Fallback for other errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=List[SubjectResponse],
    summary="Get all subjects for a student"
)
def get_student_subjects(
    student_id: UUID,
    current_user: User = Depends(get_current_user),
    use_cases: SubjectUseCases = Depends(get_subject_use_cases)
):
    """
    Get all subjects for a specific student.

    Returns both school subjects ("colegio") and extracurricular activities ("extraescolar").
    """
    try:
        subjects = use_cases.get_subjects_by_student(
            student_id=student_id,
            user_id=current_user.id
        )
        return [SubjectResponse.model_validate(s) for s in subjects]
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.get(
    "/{subject_id}",
    response_model=SubjectResponse,
    summary="Get a specific subject"
)
def get_subject(
    student_id: UUID,
    subject_id: UUID,
    current_user: User = Depends(get_current_user),
    use_cases: SubjectUseCases = Depends(get_subject_use_cases)
):
    """
    Get a specific subject by ID.

    Requires ownership verification.
    """
    try:
        subject = use_cases.get_subject_by_id(subject_id, current_user.id)

        # Verify the subject belongs to the student in the path
        if subject.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found for this student"
            )

        return SubjectResponse.model_validate(subject)
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
    "/{subject_id}",
    response_model=SubjectResponse,
    summary="Update a subject"
)
def update_subject(
    student_id: UUID,
    subject_id: UUID,
    data: SubjectUpdateRequest,
    current_user: User = Depends(get_current_user),
    use_cases: SubjectUseCases = Depends(get_subject_use_cases)
):
    """
    Update a subject.

    Only the owner can update the subject.
    All fields are optional - only provided fields will be updated.
    """
    try:
        subject = use_cases.update_subject(subject_id, current_user.id, data)

        # Verify the subject belongs to the student in the path
        if subject.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found for this student"
            )

        return SubjectResponse.model_validate(subject)
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
    "/{subject_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a subject"
)
def delete_subject(
    student_id: UUID,
    subject_id: UUID,
    current_user: User = Depends(get_current_user),
    use_cases: SubjectUseCases = Depends(get_subject_use_cases)
):
    """
    Delete a subject (soft delete).

    Only the owner can delete the subject.
    """
    try:
        # First get the subject to verify it belongs to the student
        subject = use_cases.get_subject_by_id(subject_id, current_user.id)

        # Verify the subject belongs to the student in the path
        if subject.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found for this student"
            )

        use_cases.delete_subject(subject_id, current_user.id)
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
