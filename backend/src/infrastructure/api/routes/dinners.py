"""
Dinner API Endpoints

REST API routes for dinner management with AI-powered suggestions
"""

from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.application.schemas.dinner import (
    DinnerCreateRequest,
    DinnerGenerateRequest,
    DinnerResponse,
    DinnerUpdateRequest,
    ShoppingListCategoryResponse,
    ShoppingListRequest,
    ShoppingListResponse,
)
from src.application.use_cases.dinner_use_cases import DinnerUseCases
from src.domain.models import User
from src.infrastructure.api.dependencies.auth import get_current_user
from src.infrastructure.api.dependencies.database import get_db
from src.infrastructure.repositories.dinner_repository import DinnerRepository
from src.infrastructure.repositories.menu_repository import MenuRepository
from src.infrastructure.repositories.student_repository import StudentRepository
from src.infrastructure.services.gemini_service import GeminiService

router = APIRouter(prefix="/students/{student_id}/dinners", tags=["dinners"])


def get_dinner_use_cases(db: Session = Depends(get_db)) -> DinnerUseCases:
    """Dependency to get DinnerUseCases instance"""
    dinner_repo = DinnerRepository(db)
    menu_repo = MenuRepository(db)
    student_repo = StudentRepository(db)
    gemini_service = GeminiService()
    return DinnerUseCases(dinner_repo, menu_repo, student_repo, gemini_service)


@router.post(
    "/generate",
    response_model=List[DinnerResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate dinner suggestions with AI",
)
async def generate_dinners(
    student_id: UUID,
    data: DinnerGenerateRequest,
    current_user: User = Depends(get_current_user),
    use_cases: DinnerUseCases = Depends(get_dinner_use_cases),
):
    """
    Generate dinner suggestions using AI based on school menus.

    - **type**: "today" for single day or "week" for 7 days
    - **target_date**: Optional specific date (defaults to today)

    The AI will:
    - Consider school lunch menus for the day/week
    - Respect allergies and excluded foods from student profile
    - Create balanced, complementary dinner suggestions
    - For days without school menu (weekends), analyze the week for nutritional balance
    """
    try:
        dinners = await use_cases.generate_dinner_suggestions(student_id=student_id, user_id=current_user.id, data=data)
        return [DinnerResponse.model_validate(d) for d in dinners]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error generating dinners: {str(e)}"
        )


@router.post("", response_model=DinnerResponse, status_code=status.HTTP_201_CREATED, summary="Create a dinner manually")
def create_dinner(
    student_id: UUID,
    data: DinnerCreateRequest,
    current_user: User = Depends(get_current_user),
    use_cases: DinnerUseCases = Depends(get_dinner_use_cases),
):
    """
    Create a dinner manually without AI.

    - **date**: Date for the dinner
    - **meal**: Meal description
    - **ingredients**: List of ingredients
    """
    try:
        dinner = use_cases.create_dinner(student_id=student_id, user_id=current_user.id, data=data)
        return DinnerResponse.model_validate(dinner)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("", response_model=List[DinnerResponse], summary="Get all dinners for a student")
def get_dinners(
    student_id: UUID,
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    current_user: User = Depends(get_current_user),
    use_cases: DinnerUseCases = Depends(get_dinner_use_cases),
):
    """
    Get all dinners for a student.

    Optionally filter by date range using start_date and end_date query parameters.
    """
    try:
        dinners = use_cases.get_dinners_for_student(
            student_id=student_id, user_id=current_user.id, start_date=start_date, end_date=end_date
        )
        return [DinnerResponse.model_validate(d) for d in dinners]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/{dinner_id}", response_model=DinnerResponse, summary="Update a dinner")
def update_dinner(
    student_id: UUID,
    dinner_id: UUID,
    data: DinnerUpdateRequest,
    current_user: User = Depends(get_current_user),
    use_cases: DinnerUseCases = Depends(get_dinner_use_cases),
):
    """
    Update an existing dinner.

    All fields are optional - only provided fields will be updated.
    """
    try:
        dinner = use_cases.update_dinner(dinner_id=dinner_id, student_id=student_id, user_id=current_user.id, data=data)
        return DinnerResponse.model_validate(dinner)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{dinner_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a dinner")
def delete_dinner(
    student_id: UUID,
    dinner_id: UUID,
    current_user: User = Depends(get_current_user),
    use_cases: DinnerUseCases = Depends(get_dinner_use_cases),
):
    """
    Delete a dinner (soft delete).
    """
    try:
        use_cases.delete_dinner(dinner_id=dinner_id, student_id=student_id, user_id=current_user.id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/shopping-list", response_model=ShoppingListResponse, summary="Generate shopping list from dinners")
async def generate_shopping_list(
    student_id: UUID,
    request: ShoppingListRequest,
    current_user: User = Depends(get_current_user),
    use_cases: DinnerUseCases = Depends(get_dinner_use_cases),
):
    """
    Generate a categorized shopping list from planned dinners using AI.

    - **scope**: "today", "week", or "custom"
    - **start_date**: Required for custom scope
    - **end_date**: Required for custom scope

    Returns a shopping list organized by categories (Meats, Vegetables, Dairy, etc.)
    """
    try:
        categories = await use_cases.generate_shopping_list(
            student_id=student_id, user_id=current_user.id, request=request
        )

        return ShoppingListResponse(categories=[ShoppingListCategoryResponse(**cat) for cat in categories])
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error generating shopping list: {str(e)}"
        )
