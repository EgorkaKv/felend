"""
Скрипт для добавления начальных категорий в базу данных

Запуск: python scripts/seed_categories.py
"""
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.models import Category
from datetime import datetime


def seed_categories():
    """Добавить начальные категории"""
    db = SessionLocal()
    
    try:
        # Проверяем, есть ли уже категории
        existing_count = db.query(Category).count()
        if existing_count > 0:
            print(f"В базе уже есть {existing_count} категорий. Пропускаем...")
            return
        
        # Начальные категории
        categories = [
            {
                "name": "Образование",
                "description": "Опросы, связанные с образованием, обучением и академической жизнью",
                "is_active": True
            },
            {
                "name": "Технологии",
                "description": "Опросы о технологиях, IT, программировании и цифровых инструментах",
                "is_active": True
            },
            {
                "name": "Здоровье",
                "description": "Опросы о здоровье, медицине, физической активности и благополучии",
                "is_active": True
            },
            {
                "name": "Бизнес",
                "description": "Опросы о бизнесе, предпринимательстве, маркетинге и экономике",
                "is_active": True
            },
            {
                "name": "Развлечения",
                "description": "Опросы о фильмах, музыке, играх, хобби и развлечениях",
                "is_active": True
            },
            {
                "name": "Общество",
                "description": "Опросы о социальных вопросах, культуре и общественной жизни",
                "is_active": True
            },
            {
                "name": "Наука",
                "description": "Опросы о научных исследованиях, экспериментах и открытиях",
                "is_active": True
            },
            {
                "name": "Путешествия",
                "description": "Опросы о путешествиях, туризме и географии",
                "is_active": True
            },
            {
                "name": "Спорт",
                "description": "Опросы о спорте, фитнесе и физической активности",
                "is_active": True
            },
            {
                "name": "Еда и кулинария",
                "description": "Опросы о еде, кулинарии, рецептах и ресторанах",
                "is_active": True
            }
        ]
        
        # Добавляем категории
        for cat_data in categories:
            category = Category(**cat_data)
            db.add(category)
        
        db.commit()
        print(f"Успешно добавлено {len(categories)} категорий:")
        
        # Показываем добавленные категории
        for cat in db.query(Category).order_by(Category.name).all():
            print(f"  - {cat.id}: {cat.name}")
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка при добавлении категорий: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_categories()
