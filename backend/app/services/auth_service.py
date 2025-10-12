from typing import Tuple
from sqlalchemy.orm import Session
from app.models import User, BalanceTransaction, TransactionType, GoogleAccount
from app.repositories.user_repository import user_repository
from app.core.security import verify_password, create_access_token, create_refresh_token, verify_token
from app.core.exceptions import (
    UserAlreadyExistsException, 
    InvalidCredentialsException, 
    UserNotFoundException,
    AuthenticationException
)
from app.core.config import settings


class AuthService:
    def __init__(self):
        self.user_repo = user_repository

    def register_user(self, db: Session, email: str, password: str, full_name: str) -> User:
        """Регистрация нового пользователя"""
        # Проверяем существование пользователя
        if self.user_repo.email_exists(db, email):
            raise UserAlreadyExistsException()
        
        # Создаем пользователя
        user = self.user_repo.create_user(
            db=db,
            email=email,
            full_name=full_name,
            password=password
        )
        
        # Создаем транзакцию приветственного бонуса
        welcome_transaction = BalanceTransaction(
            user_id=user.id,
            transaction_type=TransactionType.BONUS,
            amount=settings.WELCOME_BONUS_POINTS,
            balance_after=user.balance,
            description="Welcome bonus for new user"
        )
        db.add(welcome_transaction)
        db.commit()
        
        return user

    def authenticate_user(self, db: Session, email: str, password: str) -> User:
        """Аутентификация пользователя по email и паролю"""
        user = self.user_repo.get_by_email(db, email)
        
        if not user or not user.hashed_password:
            raise InvalidCredentialsException()
        
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()
        
        if not user.is_active:
            raise AuthenticationException("Account is deactivated")
        
        return user

    def create_tokens(self, user: User) -> Tuple[str, str]:
        """Создание access и refresh токенов"""
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        return access_token, refresh_token

    def refresh_access_token(self, db: Session, refresh_token: str) -> Tuple[str, str]:
        """Обновление access токена через refresh токен"""
        payload = verify_token(refresh_token, token_type="refresh")
        
        if not payload:
            raise AuthenticationException("Invalid refresh token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException("Invalid token payload")
        
        user = self.user_repo.get(db, int(user_id))
        if not user or not user.is_active:
            raise UserNotFoundException()
        
        # Создаем новые токены
        return self.create_tokens(user)

    def get_current_user(self, db: Session, token: str) -> User:
        """Получение текущего пользователя по access токену"""
        payload = verify_token(token, token_type="access")
        
        if not payload:
            raise AuthenticationException("Invalid access token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException("Invalid token payload")
        
        user = self.user_repo.get(db, int(user_id))
        if not user or not user.is_active:
            raise UserNotFoundException()
        
        return user


# Создаем экземпляр сервиса
auth_service = AuthService()