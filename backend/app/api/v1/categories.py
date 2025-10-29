from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.repositories.category_repository import category_repository
from app.schemas import CategoryResponse, CategoryListResponse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(
    "",
    response_model=CategoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить список категорий",
    description="Получить список всех активных категорий, отсортированных по имени. Публичный эндпоинт, не требует авторизации.",
)
async def get_categories(
    db: Session = Depends(get_db)
) -> CategoryListResponse:
    """
    Получить список всех активных категорий.
    
    **Возвращает:**
    - Список активных категорий, отсортированных по имени
    - Общее количество категорий
    
    **Примечания:**
    - Публичный эндпоинт, не требует авторизации
    - Возвращает только категории с is_active=True
    - Сортировка по алфавиту (по полю name)
    """
    categories = category_repository.get_all_active(db)
    
    return CategoryListResponse(
        categories=[CategoryResponse.model_validate(cat, from_attributes=True) for cat in categories],
        total=len(categories)
    )
