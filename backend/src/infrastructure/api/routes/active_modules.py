"""
Active Modules API Endpoints

REST API routes for active modules management
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.application.schemas.active_modules import ActiveModulesResponse, ActiveModulesUpdateRequest
from src.application.use_cases.active_modules_use_cases import ActiveModulesUseCases
from src.domain.models import User
from src.infrastructure.api.dependencies.auth import get_current_user
from src.infrastructure.api.dependencies.database import get_db
from src.infrastructure.repositories.active_modules_repository import ActiveModulesRepository
from src.infrastructure.repositories.student_repository import StudentRepository

router = APIRouter(prefix="/students/{student_id}/active-modules", tags=["active-modules"])


def get_active_modules_use_cases(db: Session = Depends(get_db)) -> ActiveModulesUseCases:
    """Dependency to get ActiveModulesUseCases instance"""
    active_modules_repo = ActiveModulesRepository(db)
    student_repo = StudentRepository(db)
    return ActiveModulesUseCases(active_modules_repo, student_repo)


@router.get("", response_model=ActiveModulesResponse, summary="Get active modules configuration")
def get_active_modules(
    student_id: UUID,
    current_user: User = Depends(get_current_user),
    use_cases: ActiveModulesUseCases = Depends(get_active_modules_use_cases),
):
    """
    Get active modules configuration for a student.

    Returns the current configuration of which modules are visible/active.
    """
    try:
        active_modules = use_cases.get_active_modules(student_id, current_user.id)
        return ActiveModulesResponse.model_validate(active_modules)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("", response_model=ActiveModulesResponse, summary="Update active modules configuration")
def update_active_modules(
    student_id: UUID,
    data: ActiveModulesUpdateRequest,
    current_user: User = Depends(get_current_user),
    use_cases: ActiveModulesUseCases = Depends(get_active_modules_use_cases),
):
    """
    Update active modules configuration for a student.

    Allows toggling which modules are visible/active in the UI.
    All fields are optional - only provided fields will be updated.

    - **subjects**: Show/hide subjects module
    - **exams**: Show/hide exams module
    - **menu**: Show/hide menu module
    - **events**: Show/hide events module
    - **dinner**: Show/hide dinner suggestions module
    - **contacts**: Show/hide contacts module
    """
    try:
        updated = use_cases.update_active_modules(student_id, current_user.id, data)
        return ActiveModulesResponse.model_validate(updated)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
