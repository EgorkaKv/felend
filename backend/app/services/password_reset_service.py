"""
Password Reset Service - бизнес-логика сброса пароля
"""
from typing import Tuple
from sqlalchemy.orm import Session
from app.repositories.email_verification_repository import email_verification_repository
from app.repositories.user_repository import user_repository
from app.services.email_service import email_service
from app.core.exceptions import (
    UserNotFoundException,
    VerificationTokenInvalidException,
    VerificationTokenExpiredException,
    InvalidVerificationCodeException,
    TooManyAttemptsException,
    VerificationRateLimitException,
    VerificationAlreadyUsedException
)
from app.core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)


class PasswordResetService:
    """Сервис для обработки сброса пароля"""
    
    MAX_ATTEMPTS = 5
    MAX_REQUESTS_PER_HOUR = 3  # Максимум 3 запроса на сброс в час
    RATE_LIMIT_SECONDS = 60  # 1 минута между отправками кода
    CODE_VALIDITY_MINUTES = 15
    
    def __init__(self, db: Session):
        self.db = db
        self.verification_repo = email_verification_repository
        self.user_repo = user_repository
        self.email_service = email_service
    
    def request_password_reset(self, email: str) -> Tuple[str, str]:
        """
        Запросить сброс пароля
        
        Args:
            email: Email пользователя
            
        Returns:
            Tuple[success_message, masked_email]
        
        Raises:
            UserNotFoundException: Пользователь не найден
            VerificationRateLimitException: Слишком много запросов
        """
        # Найти пользователя по email
        user = self.user_repo.get_by_email(self.db, email)
        
        # Для безопасности не говорим, что пользователь не найден
        # Просто молча выходим (чтобы злоумышленники не могли узнать существующие email)
        if not user:
            masked_email = self.email_service.mask_email(email)
            logger.warning(f"Password reset requested for non-existent email: {masked_email}")
            return (
                f"If this email is registered, a password reset code will be sent to {masked_email}",
                masked_email
            )
        
        # Проверить rate limiting (не более 3 запросов в час)
        recent_requests = self.verification_repo.count_recent_password_resets(
            self.db,
            user.id,
            time_window_minutes=60
        )
        
        if recent_requests >= self.MAX_REQUESTS_PER_HOUR:
            raise VerificationRateLimitException(
                retry_after_seconds=3600  # 1 час
            )
        
        # Проверить, есть ли активный запрос на сброс
        existing_reset = self.verification_repo.get_active_password_reset_by_user_id(
            self.db, 
            user.id
        )
        
        # Если есть активный запрос, проверить rate limiting для повторной отправки
        if existing_reset and not self.verification_repo.can_request_new_code(
            existing_reset,
            self.RATE_LIMIT_SECONDS
        ):
            raise VerificationRateLimitException(self.RATE_LIMIT_SECONDS)
        
        # Если нет активного запроса, создать новый
        if not existing_reset:
            existing_reset = self.verification_repo.create_password_reset(
                db=self.db,
                user_id=user.id,
                token_validity_hours=1  # Токен действителен 1 час
            )
        
        # Сгенерировать новый код
        code = self.verification_repo.generate_verification_code(
            self.db,
            existing_reset.id,
            code_validity_minutes=self.CODE_VALIDITY_MINUTES
        )
        
        # Отправить код на email
        email_sent = self.email_service.send_password_reset_code(user.email, code)
        
        if not email_sent:
            logger.error(f"Failed to send password reset email to {user.email}")
        
        # Маскировать email для ответа
        masked_email = self.email_service.mask_email(user.email)
        
        logger.info(f"Password reset code sent to user {user.id} ({masked_email})")
        
        return (
            f"Password reset code sent to {masked_email}. Code valid for {self.CODE_VALIDITY_MINUTES} minutes.",
            masked_email
        )
    
    def reset_password(
        self, 
        email: str, 
        code: str, 
        new_password: str
    ) -> dict:
        """
        Сбросить пароль с использованием кода
        
        Args:
            email: Email пользователя
            code: 6-значный код
            new_password: Новый пароль
            
        Returns:
            dict: Данные пользователя
            
        Raises:
            UserNotFoundException: Пользователь не найден
            InvalidVerificationCodeException: Неверный код
            TooManyAttemptsException: Слишком много попыток
            VerificationTokenExpiredException: Код истёк
        """
        # Найти пользователя
        user = self.user_repo.get_by_email(self.db, email)
        if not user:
            raise UserNotFoundException(email=email)
        
        # Получить активный запрос на сброс
        reset_request = self.verification_repo.get_active_password_reset_by_user_id(
            self.db, 
            user.id
        )
        
        if not reset_request:
            raise VerificationTokenInvalidException("No active password reset request found")
        
        # Проверить, не истек ли токен
        if not self.verification_repo.is_token_valid(reset_request):
            raise VerificationTokenExpiredException("Password reset request expired")
        
        # Проверить, не был ли уже использован
        if reset_request.is_used:
            raise VerificationAlreadyUsedException()
        
        # Проверить количество попыток
        if reset_request.attempts >= self.MAX_ATTEMPTS:
            raise TooManyAttemptsException(self.MAX_ATTEMPTS)
        
        # Проверить, не истек ли код
        if not self.verification_repo.is_code_valid(reset_request):
            self.verification_repo.increment_attempts(self.db, reset_request.id)
            attempts_left = self.MAX_ATTEMPTS - reset_request.attempts - 1
            raise InvalidVerificationCodeException(attempts_left)
        
        # Проверить код
        if reset_request.verification_code != code:
            self.verification_repo.increment_attempts(self.db, reset_request.id)
            attempts_left = self.MAX_ATTEMPTS - reset_request.attempts - 1
            
            if attempts_left <= 0:
                raise TooManyAttemptsException(self.MAX_ATTEMPTS)
            
            raise InvalidVerificationCodeException(attempts_left)
        
        # Код правильный! Сбросить пароль
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        self.db.refresh(user)
        
        # Пометить запрос как использованный
        self.verification_repo.mark_as_used(self.db, reset_request.id)
        
        logger.info(f"User {user.id} ({user.email}) successfully reset password")
        
        # Вернуть данные пользователя
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "message": "Password successfully reset"
        }


# Для использования в dependency injection
def get_password_reset_service(db: Session) -> PasswordResetService:
    return PasswordResetService(db)
