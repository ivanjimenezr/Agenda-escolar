"""
Exam API Endpoints

REST API routes for exam management
"""

from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.application.schemas.exam import ExamCreateRequest, ExamResponse, ExamUpdateRequest
from src.application.use_cases.exam_use_cases import ExamUseCases
from src.domain.models import User
from src.infrastructure.api.dependencies.auth import get_current_user
from src.infrastructure.api.dependencies.database import get_db
from src.infrastructure.repositories.exam_repository import ExamRepository
from src.infrastructure.repositories.student_repository import StudentRepository

router = APIRouter(prefix="/students/{student_id}/exams", tags=["exams"])


def get_exam_use_cases(db: Session = Depends(get_db)) -> ExamUseCases:
    """Dependency to get ExamUseCases instance"""
    exam_repo = ExamRepository(db)
    student_repo = StudentRepository(db)
    return ExamUseCases(exam_repo, student_repo)


@router.post("", response_model=ExamResponse, status_code=status.HTTP_201_CREATED, summary="Create a new exam")
def create_exam(
    student_id: UUID,
    data: ExamCreateRequest,
    current_user: User = Depends(get_current_user),
    use_cases: ExamUseCases = Depends(get_exam_use_cases),
):
    """
    Create a new exam for a student.

    - **student_id**: UUID of the student (from path)
    - **subject**: Subject name (e.g., "Matemáticas", "Lengua")
    - **date**: Exam date (YYYY-MM-DD format)
    - **topic**: Exam topic or description
    - **notes**: Optional additional notes
    """
    # If student_id missing in body, fill it from the path; otherwise ensure they match
    if getattr(data, "student_id", None) is None:
        data = data.model_copy(update={"student_id": student_id})
    elif data.student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Student ID in path must match student_id in request body"
        )

    try:
        exam = use_cases.create_exam(current_user.id, data)
        return ExamResponse.model_validate(exam)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[ExamResponse], summary="Get all exams for a student")
def get_student_exams(
    student_id: UUID,
    from_date: Optional[date] = Query(None, description="Filter exams from this date onwards"),
    to_date: Optional[date] = Query(None, description="Filter exams until this date"),
    current_user: User = Depends(get_current_user),
    use_cases: ExamUseCases = Depends(get_exam_use_cases),
):
    """
    Get all exams for a specific student.

    Optionally filter by date range using from_date and to_date query parameters.
    Returns exams ordered by date (ascending).
    """
    try:
        exams = use_cases.get_exams_by_student(
            student_id=student_id, user_id=current_user.id, from_date=from_date, to_date=to_date
        )
        return [ExamResponse.model_validate(e) for e in exams]
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/{exam_id}", response_model=ExamResponse, summary="Get a specific exam")
def get_exam(
    student_id: UUID,
    exam_id: UUID,
    current_user: User = Depends(get_current_user),
    use_cases: ExamUseCases = Depends(get_exam_use_cases),
):
    """
    Get a specific exam by ID.

    Requires ownership verification.
    """
    try:
        exam = use_cases.get_exam_by_id(exam_id, current_user.id)

        # Verify the exam belongs to the student in the path
        if exam.student_id != student_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found for this student")

        return ExamResponse.model_validate(exam)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/{exam_id}", response_model=ExamResponse, summary="Update an exam")
def update_exam(
    student_id: UUID,
    exam_id: UUID,
    data: ExamUpdateRequest,
    current_user: User = Depends(get_current_user),
    use_cases: ExamUseCases = Depends(get_exam_use_cases),
):
    """
    Update an exam.

    Only the owner can update the exam.
    All fields are optional - only provided fields will be updated.
    """
    try:
        exam = use_cases.update_exam(exam_id, current_user.id, data)

        # Verify the exam belongs to the student in the path
        if exam.student_id != student_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found for this student")

        return ExamResponse.model_validate(exam)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an exam")
def delete_exam(
    student_id: UUID,
    exam_id: UUID,
    current_user: User = Depends(get_current_user),
    use_cases: ExamUseCases = Depends(get_exam_use_cases),
):
    """
    Delete an exam (hard delete - permanent).

    Only the owner can delete the exam.
    """
    try:
        # First get the exam to verify it belongs to the student
        exam = use_cases.get_exam_by_id(exam_id, current_user.id)

        # Verify the exam belongs to the student in the path
        if exam.student_id != student_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found for this student")

        use_cases.delete_exam(exam_id, current_user.id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
