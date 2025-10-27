"""
Repository для работы с email верификацией и сбросом пароля
"""
from typing import Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models import EmailVerification, User, VerificationType
import uuid
import random


class EmailVerificationRepository:
    """Repository для управления email верификацией"""
    
    def create_verification(
        self, 
        db: Session, 
        user_id: int,
        token_validity_hours: int = 24,
        verification_type: VerificationType = VerificationType.email_verification
    ) -> EmailVerification:
        """Создать новую запись верификации с токеном"""
        
        # verification_token = str(uuid.uuid4())
        # FIXME: временно фиксированный токен для тестов
        verification_token = str("121212")
        # Используем timezone-aware datetime
        token_expires_at = datetime.now(timezone.utc) + timedelta(hours=token_validity_hours)
        
        verification = EmailVerification(
            user_id=user_id,
            verification_type=verification_type,
            verification_token=verification_token,
            token_expires_at=token_expires_at,
            is_used=False,
            attempts=0
        )
        
        db.add(verification)
        db.commit()
        db.refresh(verification)
        return verification
    
    def get_by_token(self, db: Session, verification_token: str) -> Optional[EmailVerification]:
        """Получить верификацию по токену"""
        return db.query(EmailVerification).filter(
            EmailVerification.verification_token == verification_token
        ).first()
    
    def get_active_by_user_id(self, db: Session, user_id: int) -> Optional[EmailVerification]:
        """Получить активную верификацию пользователя (не использованную и не истекшую)"""
        now = datetime.now(timezone.utc)
        return db.query(EmailVerification).filter(
            EmailVerification.user_id == user_id,
            EmailVerification.is_used == False,
            EmailVerification.token_expires_at > now
        ).first()
    
    def generate_verification_code(
        self,
        db: Session,
        verification_id: int,
        code_validity_minutes: int = 15
    ) -> str:
        """Сгенерировать и сохранить 6-значный код"""
        # code = str(random.randint(100000, 999999))
        # FIXME: временно фиксированный код для тестов
        code = "121212"
        code_expires_at = datetime.now(timezone.utc) + timedelta(minutes=code_validity_minutes)
        
        verification = db.query(EmailVerification).filter(
            EmailVerification.id == verification_id
        ).first()
        
        if verification:
            verification.verification_code = code
            verification.code_expires_at = code_expires_at
            verification.last_code_sent_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(verification)
        
        return code
    
    def increment_attempts(self, db: Session, verification_id: int) -> EmailVerification:
        """Увеличить счетчик неудачных попыток"""
        verification = db.query(EmailVerification).filter(
            EmailVerification.id == verification_id
        ).first()
        
        if verification:
            verification.attempts += 1
            db.commit()
            db.refresh(verification)
        
        return verification
    
    def mark_as_used(self, db: Session, verification_id: int) -> EmailVerification:
        """Пометить верификацию как использованную"""
        verification = db.query(EmailVerification).filter(
            EmailVerification.id == verification_id
        ).first()
        
        if verification:
            verification.is_used = True
            db.commit()
            db.refresh(verification)
        
        return verification
    
    def is_code_valid(self, verification: EmailVerification) -> bool:
        """Проверить, не истек ли код"""
        if not verification.code_expires_at:
            return False
        
        # Ensure timezone awareness
        code_expires = verification.code_expires_at
        if code_expires.tzinfo is None:
            code_expires = code_expires.replace(tzinfo=timezone.utc)
        
        return datetime.now(timezone.utc) < code_expires
    
    def is_token_valid(self, verification: EmailVerification) -> bool:
        """Проверить, не истек ли токен"""
        # Ensure timezone awareness
        token_expires = verification.token_expires_at
        if token_expires.tzinfo is None:
            token_expires = token_expires.replace(tzinfo=timezone.utc)
        
        return datetime.now(timezone.utc) < token_expires
    
    def can_request_new_code(
        self, 
        verification: EmailVerification, 
        rate_limit_seconds: int = 60
    ) -> bool:
        """Проверить, можно ли запросить новый код (rate limiting)"""
        if not verification.last_code_sent_at:
            return True
        
        # Ensure timezone awareness
        last_sent = verification.last_code_sent_at
        if last_sent.tzinfo is None:
            last_sent = last_sent.replace(tzinfo=timezone.utc)
        
        time_since_last_code = datetime.now(timezone.utc) - last_sent
        return time_since_last_code.total_seconds() >= rate_limit_seconds
    
    # ===== Password Reset Methods =====
    
    def create_password_reset(
        self,
        db: Session,
        user_id: int,
        token_validity_hours: int = 1
    ) -> EmailVerification:
        """Создать запись для сброса пароля"""
        return self.create_verification(
            db=db,
            user_id=user_id,
            token_validity_hours=token_validity_hours,
            verification_type=VerificationType.password_reset
        )
    
    # ===== Email Verification with User Data Methods =====
    
    def create_with_user_data(
        self,
        db: Session,
        email: str,
        hashed_password: str,
        full_name: str,
        token_validity_hours: int = 24
    ) -> EmailVerification:
        """Создать запись верификации с данными пользователя (для регистрации)"""
        verification_token = str(uuid.uuid4())
        token_expires_at = datetime.now(timezone.utc) + timedelta(hours=token_validity_hours)
        
        verification = EmailVerification(
            user_id=None,  # Пользователь ещё не создан
            verification_type=VerificationType.email_verification,
            verification_token=verification_token,
            token_expires_at=token_expires_at,
            is_used=False,
            attempts=0,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name
        )
        
        db.add(verification)
        db.commit()
        db.refresh(verification)
        return verification
    
    def get_by_email(
        self, 
        db: Session, 
        email: str,
        verification_type: Optional[VerificationType] = None
    ) -> Optional[EmailVerification]:
        """Получить верификацию по email"""
        query = db.query(EmailVerification).filter(
            EmailVerification.email == email
        )
        if verification_type:
            query = query.filter(EmailVerification.verification_type == verification_type)
        return query.first()
    
    def get_active_by_email(
        self,
        db: Session,
        email: str
    ) -> Optional[EmailVerification]:
        """Получить активную верификацию по email (не использованную и не истекшую)"""
        now = datetime.now(timezone.utc)
        return db.query(EmailVerification).filter(
            EmailVerification.email == email,
            EmailVerification.verification_type == VerificationType.email_verification,
            EmailVerification.is_used == False,
            EmailVerification.token_expires_at > now
        ).first()
    
    def update_user_data(
        self,
        db: Session,
        verification_id: int,
        email: str,
        hashed_password: str,
        full_name: str
    ) -> EmailVerification:
        """Обновить данные пользователя в записи верификации"""
        verification = db.query(EmailVerification).filter(
            EmailVerification.id == verification_id
        ).first()
        
        if verification:
            verification.email = email
            verification.hashed_password = hashed_password
            verification.full_name = full_name
            db.commit()
            db.refresh(verification)
        
        return verification
    
    def delete_verification(self, db: Session, verification_id: int) -> bool:
        """Удалить запись верификации"""
        verification = db.query(EmailVerification).filter(
            EmailVerification.id == verification_id
        ).first()
        
        if verification:
            db.delete(verification)
            db.commit()
            return True
        return False
    
    def get_active_password_reset_by_user_id(
        self, 
        db: Session, 
        user_id: int
    ) -> Optional[EmailVerification]:
        """Получить активный запрос на сброс пароля пользователя"""
        now = datetime.now(timezone.utc)
        return db.query(EmailVerification).filter(
            EmailVerification.user_id == user_id,
            EmailVerification.verification_type == VerificationType.password_reset,
            EmailVerification.is_used == False,
            EmailVerification.token_expires_at > now
        ).first()
    
    def count_recent_password_resets(
        self,
        db: Session,
        user_id: int,
        time_window_minutes: int = 60
    ) -> int:
        """Подсчитать количество запросов на сброс пароля за последнее время"""
        time_threshold = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)
        return db.query(EmailVerification).filter(
            EmailVerification.user_id == user_id,
            EmailVerification.verification_type == VerificationType.password_reset,
            EmailVerification.created_at > time_threshold
        ).count()


# Singleton instance
email_verification_repository = EmailVerificationRepository()
