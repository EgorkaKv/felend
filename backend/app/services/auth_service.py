
from typing import Tuple
from sqlalchemy.orm import Session
from app.models import User, BalanceTransaction, TransactionType
from app.repositories.user_repository import user_repository
from app.repositories.email_verification_repository import email_verification_repository
from app.core.security import verify_password, create_access_token, create_refresh_token, verify_token, get_password_hash
from app.core.exceptions import (
    InvalidTokenException,
    UserAlreadyExistsException, 
    InvalidCredentialsException, 
    UserNotFoundException,
    AuthenticationException,
    UserInactiveException
)
from app.core.config import settings


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = user_repository
        self.verification_repo = email_verification_repository
        self.db = db

    def register_user(self, email: str, password: str, full_name: str) -> Tuple[str, str]:
        """
        Регистрация нового пользователя
        
        Теперь данные пользователя сохраняются только в email_verifications
        до подтверждения email. Пользователь создаётся только после верификации.
        
        Returns:
            Tuple[verification_token, masked_email] - токен верификации и маскированный email
        """
        from app.services.email_service import email_service
        
        # Проверяем существование email в обеих таблицах
        if self.user_repo.email_exists_anywhere(self.db, email):
            # Проверяем, может быть это pending registration
            existing_verification = self.verification_repo.get_active_by_email(self.db, email)
            
            if existing_verification:
                # Обновляем существующую pending registration
                hashed_password = get_password_hash(password)
                self.verification_repo.update_user_data(
                    self.db,
                    existing_verification.id,
                    email,
                    hashed_password,
                    full_name
                )
                return existing_verification.verification_token, email_service.mask_email(email)
            else:
                # Email уже зарегистрирован и подтверждён
                raise UserAlreadyExistsException(email)
        
        # Хешируем пароль
        hashed_password = get_password_hash(password)
        
        # Создаем запись верификации с данными пользователя
        verification = self.verification_repo.create_with_user_data(
            db=self.db,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            token_validity_hours=24
        )
        
        return verification.verification_token, email_service.mask_email(email)

    def authenticate_user(self, email: str, password: str) -> User:
        user = self.user_repo.get_by_email(self.db, email)
        if not user or not user.hashed_password:
            raise InvalidCredentialsException()
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()
        if not user.is_active:
            raise UserInactiveException(user.id)  # Не даем войти неактивным пользователям
        return user
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()
        if not user.is_active:
            raise AuthenticationException("Account is deactivated")
        return user

    def create_tokens(self, user: User) -> Tuple[str, str]:
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        return access_token, refresh_token

    def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        payload = verify_token(refresh_token, token_type="refresh")
        if not payload:
            raise AuthenticationException("Invalid refresh token")
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException("Invalid token payload")
        user = self.user_repo.get(self.db, int(user_id))
        if not user or not user.is_active:
            raise UserNotFoundException()
        return self.create_tokens(user)

    def get_current_user(self, token: str) -> User:
        payload = verify_token(token, token_type="access")

        if not payload:
            raise InvalidTokenException()
        
        user_id = payload.get("sub")

        if not user_id:
            raise InvalidTokenException()
        
        user = self.user_repo.get(self.db, int(user_id))
        
        if not user:
            raise UserNotFoundException()
        return user