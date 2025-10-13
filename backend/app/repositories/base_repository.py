from typing import Generic, TypeVar, Type, Optional, List, Any, Dict, Protocol
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel


class HasId(Protocol):
    """Protocol для объектов с id атрибутом"""
    id: int


# Определяем базовый тип для моделей SQLAlchemy
ModelType = TypeVar("ModelType", bound=HasId)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        Базовый репозиторий с CRUD операциями
        
        Args:
            model: SQLAlchemy модель
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Получить объект по ID"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """Получить список объектов с фильтрами и пагинацией"""
        query = db.query(self.model)
        
        # Применяем фильтры
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, list):
                        query = query.filter(getattr(self.model, key).in_(value))
                    else:
                        query = query.filter(getattr(self.model, key) == value)
        
        # Сортировка
        if order_by and hasattr(self.model, order_by):
            query = query.order_by(getattr(self.model, order_by))
        
        return query.offset(skip).limit(limit).all()

    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """Подсчет количества записей с фильтрами"""
        query = db.query(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, list):
                        query = query.filter(getattr(self.model, key).in_(value))
                    else:
                        query = query.filter(getattr(self.model, key) == value)
        
        return query.count()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Создать новый объект"""
        obj_in_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, 
        db: Session, 
        db_obj: ModelType, 
        obj_in: UpdateSchemaType | Dict[str, Any]
    ) -> ModelType:
        """Обновить существующий объект"""
        obj_data = db_obj.__dict__
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, 'model_dump') else obj_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: Any) -> Optional[ModelType]:
        """Удалить объект по ID"""
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def get_by_field(self, db: Session, field_name: str, value: Any) -> Optional[ModelType]:
        """Получить объект по значению поля"""
        if hasattr(self.model, field_name):
            return db.query(self.model).filter(getattr(self.model, field_name) == value).first()
        return None

    def exists(self, db: Session, id: Any) -> bool:
        """Проверить существование объекта по ID"""
        return db.query(self.model).filter(self.model.id == id).first() is not None