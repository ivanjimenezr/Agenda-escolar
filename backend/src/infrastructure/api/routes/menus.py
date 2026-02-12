"""
Menu Item API Endpoints

REST API routes for school menu management
"""

from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.application.schemas.menu import MenuItemCreateRequest, MenuItemResponse, MenuItemUpdateRequest
from src.application.use_cases.menu_use_cases import MenuUseCases
from src.domain.models import User
from src.infrastructure.api.dependencies.auth import get_current_user
from src.infrastructure.api.dependencies.database import get_db
from src.infrastructure.repositories.menu_repository import MenuRepository
from src.infrastructure.repositories.student_repository import StudentRepository

router = APIRouter(prefix="/menus", tags=["menus"])


def get_menu_use_cases(db: Session = Depends(get_db)) -> MenuUseCases:
    """Dependency to get MenuUseCases instance"""
    menu_repo = MenuRepository(db)
    student_repo = StudentRepository(db)
    return MenuUseCases(menu_repo, student_repo)


@router.post("", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED, summary="Create a new menu item")
def create_menu_item(
    data: MenuItemCreateRequest,
    current_user: User = Depends(get_current_user),
    use_cases: MenuUseCases = Depends(get_menu_use_cases),
):
    """
    Create a new menu item for a student.

    - **student_id**: UUID of the student
    - **date**: Date of the menu
    - **first_course**: First course (e.g., "Lentejas")
    - **second_course**: Second course (e.g., "Pollo asado")
    - **side_dish**: Optional side dish
    - **dessert**: Optional dessert
    - **allergens**: List of allergens
    """
    try:
        menu = use_cases.create_menu_item(current_user.id, data)
        return MenuItemResponse.model_validate(menu)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/student/{student_id}", response_model=List[MenuItemResponse], summary="Get all menu items for a student")
def get_student_menus(
    student_id: UUID,
    start_date: Optional[date] = Query(None, description="Filter from this date"),
    end_date: Optional[date] = Query(None, description="Filter until this date"),
    current_user: User = Depends(get_current_user),
    use_cases: MenuUseCases = Depends(get_menu_use_cases),
):
    """
    Get all menu items for a specific student.

    Optional date range filtering with start_date and end_date query parameters.
    """
    try:
        menus = use_cases.get_menu_items_by_student(
            student_id=student_id, user_id=current_user.id, start_date=start_date, end_date=end_date
        )
        return [MenuItemResponse.model_validate(m) for m in menus]
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/{menu_id}", response_model=MenuItemResponse, summary="Get a specific menu item")
def get_menu_item(
    menu_id: UUID, current_user: User = Depends(get_current_user), use_cases: MenuUseCases = Depends(get_menu_use_cases)
):
    """
    Get a specific menu item by ID.

    Requires ownership verification.
    """
    try:
        menu = use_cases.get_menu_item_by_id(menu_id, current_user.id)
        return MenuItemResponse.model_validate(menu)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put(
    "/upsert", response_model=MenuItemResponse, status_code=status.HTTP_200_OK, summary="Create or update a menu item"
)
def upsert_menu_item(
    data: MenuItemCreateRequest,
    current_user: User = Depends(get_current_user),
    use_cases: MenuUseCases = Depends(get_menu_use_cases),
):
    """
    Create or update a menu item for a specific student and date.

    If a menu already exists for the given student_id and date, it will be updated.
    Otherwise, a new menu item will be created.

    - **student_id**: UUID of the student
    - **date**: Date of the menu
    - **first_course**: First course (e.g., "Lentejas")
    - **second_course**: Second course (e.g., "Pollo asado")
    - **side_dish**: Optional side dish
    - **dessert**: Optional dessert
    - **allergens**: List of allergens

    NOTE: this route must be registered before PUT /{menu_id} so that FastAPI
    matches the static path "/upsert" before the dynamic UUID path parameter.
    """
    try:
        menu = use_cases.upsert_menu_item(
            user_id=current_user.id,
            student_id=data.student_id,
            menu_date=data.date,
            first_course=data.first_course,
            second_course=data.second_course,
            side_dish=data.side_dish,
            dessert=data.dessert,
            allergens=data.allergens,
        )
        return MenuItemResponse.model_validate(menu)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/{menu_id}", response_model=MenuItemResponse, summary="Update a menu item")
def update_menu_item(
    menu_id: UUID,
    data: MenuItemUpdateRequest,
    current_user: User = Depends(get_current_user),
    use_cases: MenuUseCases = Depends(get_menu_use_cases),
):
    """
    Update a menu item.

    Only the owner can update the menu item.
    All fields are optional - only provided fields will be updated.
    """
    try:
        menu = use_cases.update_menu_item(menu_id, current_user.id, data)
        return MenuItemResponse.model_validate(menu)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a menu item")
def delete_menu_item(
    menu_id: UUID, current_user: User = Depends(get_current_user), use_cases: MenuUseCases = Depends(get_menu_use_cases)
):
    """
    Delete a menu item (soft delete).

    Only the owner can delete the menu item.
    """
    try:
        use_cases.delete_menu_item(menu_id, current_user.id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
