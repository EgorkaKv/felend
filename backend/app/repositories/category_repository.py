from typing import List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel
from app.models import Category
from app.repositories.base_repository import BaseRepository
from app.schemas import CategoryResponse


# Заглушки для generic типов, так как у Category нет Create/Update схем
class _DummySchema(BaseModel):
    pass


class CategoryRepository(BaseRepository[Category, _DummySchema, _DummySchema]):
    def __init__(self):
        super().__init__(Category)

    def get_all_active(self, db: Session) -> List[Category]:
        """Получить все активные категории, отсортированные по имени"""
        return (
            db.query(Category)
            .filter(Category.is_active == True)
            .order_by(Category.name)
            .all()
        )

    def get_by_ids(self, db: Session, category_ids: List[int]) -> List[Category]:
        """Получить категории по списку ID"""
        return (
            db.query(Category)
            .filter(Category.id.in_(category_ids))
            .all()
        )

    def validate_category_ids(self, db: Session, category_ids: List[int]) -> bool:
        """Проверить, что все ID категорий существуют и активны"""
        if not category_ids:
            return True
        
        found_categories = self.get_by_ids(db, category_ids)
        
        # Проверяем, что найдены все категории и они активны
        if len(found_categories) != len(category_ids):
            return False
        
        return all(cat.is_active for cat in found_categories)

    def get_active_by_ids(self, db: Session, category_ids: List[int]) -> List[Category]:
        """Получить только активные категории по списку ID"""
        return (
            db.query(Category)
            .filter(Category.id.in_(category_ids))
            .filter(Category.is_active == True)
            .all()
        )


# Создаем singleton instance
category_repository = CategoryRepository()
