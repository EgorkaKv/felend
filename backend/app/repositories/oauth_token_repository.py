"""
Repository для работы с одноразовыми OAuth токенами
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models import OAuthTemporaryToken
import uuid


class OAuthTokenRepository:
    """Репозиторий для управления одноразовыми OAuth токенами"""
    
    def create_token(self, db: Session, user_id: int, ttl_minutes: int = 5) -> str:
        """
        Создать одноразовый токен для пользователя
        
        Args:
            db: Сессия БД
            user_id: ID пользователя
            ttl_minutes: Время жизни токена в минутах (по умолчанию 5)
        
        Returns:
            str: Сгенерированный токен (UUID)
        """
        token = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
        
        oauth_token = OAuthTemporaryToken(
            token=token,
            user_id=user_id,
            is_used=False,
            expires_at=expires_at
        )
        
        db.add(oauth_token)
        db.commit()
        db.refresh(oauth_token)
        
        return token
    
    def get_by_token(self, db: Session, token: str) -> Optional[OAuthTemporaryToken]:
        """
        Получить токен по значению
        
        Args:
            db: Сессия БД
            token: Значение токена (UUID)
        
        Returns:
            Optional[OAuthTemporaryToken]: Объект токена или None
        """
        return db.query(OAuthTemporaryToken).filter(
            OAuthTemporaryToken.token == token
        ).first()
    
    def mark_as_used(self, db: Session, token_id: int) -> bool:
        """
        Пометить токен как использованный
        
        Args:
            db: Сессия БД
            token_id: ID токена
        
        Returns:
            bool: True если успешно
        """
        oauth_token = db.query(OAuthTemporaryToken).filter(
            OAuthTemporaryToken.id == token_id
        ).first()
        
        if not oauth_token:
            return False
        
        oauth_token.is_used = True
        db.commit()
        return True
    
    def is_token_valid(self, token: OAuthTemporaryToken) -> bool:
        """
        Проверить валидность токена (не использован и не истек)
        
        Args:
            token: Объект токена
        
        Returns:
            bool: True если токен валиден
        """
        if token.is_used:
            return False
        
        now = datetime.now(timezone.utc)
        
        # Ensure expires_at is timezone-aware
        if token.expires_at.tzinfo is None:
            expires_at = token.expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at = token.expires_at
        
        return expires_at > now
    
    def cleanup_expired(self, db: Session) -> int:
        """
        Удалить все истекшие и использованные токены
        
        Args:
            db: Сессия БД
        
        Returns:
            int: Количество удаленных токенов
        """
        now = datetime.now(timezone.utc)
        
        # Удаляем истекшие токены
        expired_count = db.query(OAuthTemporaryToken).filter(
            OAuthTemporaryToken.expires_at < now
        ).delete()
        
        # Удаляем использованные токены старше 1 часа
        one_hour_ago = now - timedelta(hours=1)
        used_count = db.query(OAuthTemporaryToken).filter(
            OAuthTemporaryToken.is_used == True,
            OAuthTemporaryToken.created_at < one_hour_ago
        ).delete()
        
        db.commit()
        
        return expired_count + used_count


# Singleton instance
oauth_token_repository = OAuthTokenRepository()
