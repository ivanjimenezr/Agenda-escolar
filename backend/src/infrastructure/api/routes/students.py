"""
Student Profile API Endpoints

REST API routes for student profile management
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.application.schemas.student import StudentCreateRequest, StudentResponse, StudentUpdateRequest
from src.application.use_cases.student_use_cases import StudentUseCases
from src.domain.models import User
from src.infrastructure.api.dependencies.auth import get_current_user
from src.infrastructure.api.dependencies.database import get_db
from src.infrastructure.repositories.student_repository import StudentRepository

router = APIRouter(prefix="/students", tags=["students"])


def get_student_use_cases(db: Session = Depends(get_db)) -> StudentUseCases:
    """Dependency to get StudentUseCases instance"""
    student_repo = StudentRepository(db)
    return StudentUseCases(student_repo)


@router.post(
    "", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, summary="Create a new student profile"
)
def create_student(
    data: StudentCreateRequest,
    current_user: User = Depends(get_current_user),
    use_cases: StudentUseCases = Depends(get_student_use_cases),
):
    """
    Create a new student profile for the authenticated user.

    - **name**: Full name of the student
    - **school**: Name of the school
    - **grade**: Grade level (e.g., "5th Grade")
    - **avatar_url**: Optional URL for student avatar
    - **allergies**: List of allergies (e.g., ["gluten", "lactose"])
    - **excluded_foods**: List of excluded foods
    """
    try:
        student = use_cases.create_student(current_user.id, data)
        return StudentResponse.model_validate(student)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[StudentResponse], summary="Get all student profiles for current user")
def get_my_students(
    current_user: User = Depends(get_current_user), use_cases: StudentUseCases = Depends(get_student_use_cases)
):
    """
    Get all student profiles belonging to the authenticated user.
    """
    students = use_cases.get_students_by_user(current_user.id)
    return [StudentResponse.model_validate(s) for s in students]


@router.get("/{student_id}", response_model=StudentResponse, summary="Get a specific student profile")
def get_student(
    student_id: UUID,
    current_user: User = Depends(get_current_user),
    use_cases: StudentUseCases = Depends(get_student_use_cases),
):
    """
    Get a specific student profile by ID.

    Requires ownership verification.
    """
    try:
        student = use_cases.get_student_by_id(student_id, current_user.id)
        return StudentResponse.model_validate(student)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/{student_id}", response_model=StudentResponse, summary="Update a student profile")
def update_student(
    student_id: UUID,
    data: StudentUpdateRequest,
    current_user: User = Depends(get_current_user),
    use_cases: StudentUseCases = Depends(get_student_use_cases),
):
    """
    Update a student profile.

    Only the owner can update the student profile.
    All fields are optional - only provided fields will be updated.
    """
    try:
        student = use_cases.update_student(student_id, current_user.id, data)
        return StudentResponse.model_validate(student)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a student profile")
def delete_student(
    student_id: UUID,
    current_user: User = Depends(get_current_user),
    use_cases: StudentUseCases = Depends(get_student_use_cases),
):
    """
    Delete a student profile (soft delete).

    Only the owner can delete the student profile.
    """
    try:
        use_cases.delete_student(student_id, current_user.id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
