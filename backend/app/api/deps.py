from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.exceptions import AuthenticationException
from app.models import User
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.survey_service import SurveyService


# Security scheme для JWT токенов
security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """Dependency для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

# Dependency для получения survey_service с инжектированной сессией
def get_survey_service(db: Session = Depends(get_db)) -> SurveyService:
    return SurveyService(db)

def get_current_user(
    auth_service: AuthService = Depends(get_auth_service),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Dependency для получения текущего авторизованного пользователя"""
    try:
        token = credentials.credentials
        user = auth_service.get_current_user(token)
        return user
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.detail),
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency для получения активного пользователя"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


# Опциональная авторизация (может быть None)
def get_current_user_optional(
    auth_service: AuthService = Depends(get_auth_service),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User | None:
    """Dependency для получения пользователя (опционально)"""
    if not credentials:
        return None
    try:
        token = credentials.credentials
        user = auth_service.get_current_user(token)
        return user if user.is_active else None
    except AuthenticationException:
        return None