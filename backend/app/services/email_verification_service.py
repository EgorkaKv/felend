"""
Email Verification Service - бизнес-логика верификации email
"""
from typing import Tuple
from sqlalchemy.orm import Session
from app.repositories.email_verification_repository import email_verification_repository
from app.repositories.user_repository import user_repository
from app.services.email_service import email_service
from app.core.exceptions import (
    VerificationTokenExpiredException,
    VerificationTokenInvalidException,
    InvalidVerificationCodeException,
    TooManyAttemptsException,
    VerificationRateLimitException,
    VerificationAlreadyUsedException,
    UserNotFoundException
)
from app.core.security import create_access_token, create_refresh_token
from app.models import BalanceTransaction, TransactionType
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmailVerificationService:
    """Сервис для обработки верификации email"""
    
    MAX_ATTEMPTS = 5
    RATE_LIMIT_SECONDS = 60  # 1 минута между запросами кода
    
    def __init__(self, db: Session):
        self.db = db
        self.verification_repo = email_verification_repository
        self.user_repo = user_repository
        self.email_service = email_service
    
    def request_verification_code(self, verification_token: str) -> Tuple[str, str]:
        """
        Запросить отправку кода верификации на email
        
        Returns:
            Tuple[success_message, masked_email]
        """
        # Получить запись верификации
        verification = self.verification_repo.get_by_token(self.db, verification_token)
        
        if not verification:
            raise VerificationTokenInvalidException(verification_token)
        
        # Проверить, не истек ли токен
        if not self.verification_repo.is_token_valid(verification):
            raise VerificationTokenExpiredException(verification_token)
        
        # Проверить, не был ли уже использован
        if verification.is_used:
            raise VerificationAlreadyUsedException()
        
        # Проверить rate limiting
        if not self.verification_repo.can_request_new_code(
            verification, 
            self.RATE_LIMIT_SECONDS
        ):
            raise VerificationRateLimitException(self.RATE_LIMIT_SECONDS)
        
        # Получить пользователя
        user = self.user_repo.get(self.db, verification.user_id)
        if not user:
            raise UserNotFoundException(user_id=verification.user_id)
        
        # Сгенерировать новый код
        code = self.verification_repo.generate_verification_code(
            self.db, 
            verification.id,
            code_validity_minutes=15
        )
        
        # Отправить код на email
        email_sent = self.email_service.send_verification_code(user.email, code)
        
        if not email_sent:
            logger.error(f"Failed to send verification email to {user.email}")
            # В production можно выбросить исключение
            # raise EmailSendFailedException()
        
        # Маскировать email для ответа
        masked_email = self.email_service.mask_email(user.email)
        
        logger.info(f"Verification code sent to user {user.id} ({masked_email})")
        
        return (
            f"Verification code sent to {masked_email}. Code valid for 15 minutes.",
            masked_email
        )
    
    def verify_email(self, verification_token: str, code: str) -> Tuple[str, str, dict]:
        """
        Проверить код и активировать аккаунт
        
        Returns:
            Tuple[access_token, refresh_token, user_dict]
        """
        # Получить запись верификации
        verification = self.verification_repo.get_by_token(self.db, verification_token)
        
        if not verification:
            raise VerificationTokenInvalidException(verification_token)
        
        # Проверить, не истек ли токен
        if not self.verification_repo.is_token_valid(verification):
            raise VerificationTokenExpiredException(verification_token)
        
        # Проверить, не был ли уже использован
        if verification.is_used:
            raise VerificationAlreadyUsedException()
        
        # Проверить количество попыток
        if verification.attempts >= self.MAX_ATTEMPTS:
            raise TooManyAttemptsException(self.MAX_ATTEMPTS)
        
        # Проверить, не истек ли код
        if not self.verification_repo.is_code_valid(verification):
            self.verification_repo.increment_attempts(self.db, verification.id)
            attempts_left = self.MAX_ATTEMPTS - verification.attempts - 1
            raise InvalidVerificationCodeException(attempts_left)
        
        # Проверить код
        if verification.verification_code != code:
            self.verification_repo.increment_attempts(self.db, verification.id)
            attempts_left = self.MAX_ATTEMPTS - verification.attempts - 1
            
            if attempts_left <= 0:
                raise TooManyAttemptsException(self.MAX_ATTEMPTS)
            
            raise InvalidVerificationCodeException(attempts_left)
        
        # Код правильный! Активировать пользователя
        user = self.user_repo.get(self.db, verification.user_id)
        if not user:
            raise UserNotFoundException(user_id=verification.user_id)
        
        # Активировать пользователя
        user.is_active = True
        
        # Добавить приветственный бонус
        user.balance += settings.WELCOME_BONUS_POINTS
        
        welcome_transaction = BalanceTransaction(
            user_id=user.id,
            transaction_type=TransactionType.BONUS,
            amount=settings.WELCOME_BONUS_POINTS,
            balance_after=user.balance,
            description="Welcome bonus for email verification",
        )
        self.db.add(welcome_transaction)
        
        self.db.commit()
        self.db.refresh(user)
        
        # Пометить верификацию как использованную
        self.verification_repo.mark_as_used(self.db, verification.id)
        
        # Создать токены для входа
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        logger.info(f"User {user.id} ({user.email}) successfully verified email and activated account")
        
        # Вернуть данные пользователя
        user_dict = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "balance": user.balance,
            "respondent_code": user.respondent_code,
            "created_at": user.created_at
        }
        
        return access_token, refresh_token, user_dict


# Для использования в dependency injection
def get_email_verification_service(db: Session) -> EmailVerificationService:
    return EmailVerificationService(db)
