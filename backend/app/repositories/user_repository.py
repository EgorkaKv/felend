from typing import Optional
from sqlalchemy.orm import Session
import secrets
from app.models import User
from app.repositories.base_repository import BaseRepository
from app.schemas import UserRegister, UserUpdate
from app.core.security import get_password_hash, generate_respondent_code


class UserRepository(BaseRepository[User, UserRegister, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        return db.query(User).filter(User.email == email).first()



    def get_by_respondent_code(self, db: Session, respondent_code: str) -> Optional[User]:
        """Получить пользователя по коду респондента"""
        return db.query(User).filter(User.respondent_code == respondent_code).first()

    def create_user(
        self, 
        db: Session, 
        email: str, 
        full_name: str, 
        password: Optional[str] = None
    ) -> User:
        """Создать нового пользователя"""
        # Генерируем временный код респондента, потом обновим его на основе ID
        temp_respondent_code = f"TEMP_{secrets.token_hex(8)}"[:16]
        
        # Создаем пользователя с временным кодом
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(password) if password else None,
            balance=10,  # Приветственный бонус
            respondent_code=temp_respondent_code,
        )
        
        db.add(user)
        db.flush()  # Получаем ID без коммита
        
        # Обновляем код респондента на основе реального ID
        user.respondent_code = generate_respondent_code(user.id)
        
        db.commit()
        db.refresh(user)
        return user

    def update_balance(self, db: Session, user: User, new_balance: int) -> User:
        """Обновить баланс пользователя"""
        user.balance = new_balance
        db.commit()
        db.refresh(user)
        return user

    def email_exists(self, db: Session, email: str, exclude_id: Optional[int] = None) -> bool:
        """Проверить существование email"""
        query = db.query(User).filter(User.email == email)
        if exclude_id:
            query = query.filter(User.id != exclude_id)
        return query.first() is not None


# Создаем экземпляр репозитория
user_repository = UserRepository()