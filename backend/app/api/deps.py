from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.exceptions import AuthenticationException
from app.models import User
from app.services.auth_service import AuthService
from app.services.google_accounts_service import GoogleAccountsService
from app.services.user_service import UserService
from app.services.survey_service import SurveyService
from app.services.balance_service import BalanceService
from app.services.participation_service import ParticipationService
from app.services.google_auth_service import GoogleAuthService
import logging

logger = logging.getLogger(__name__)

# Security scheme для JWT токенов
security = HTTPBearer(auto_error=False)
optional_security = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """Dependency для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_participation_service(db: Session = Depends(get_db)) -> ParticipationService:
    return ParticipationService(db)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


# Dependency для получения survey_service с инжектированной сессией
def get_survey_service(db: Session = Depends(get_db)) -> SurveyService:
    return SurveyService(db)


def get_google_auth_service(db: Session = Depends(get_db)) -> GoogleAuthService:
    return GoogleAuthService(db)


def get_current_user(
    auth_service: AuthService = Depends(get_auth_service),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Dependency для получения текущего авторизованного пользователя"""
    if credentials is None:
        logger.warning("No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    user = auth_service.get_current_user(token)
    logger.info(f"User authorized: {user.id}")
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency для получения активного пользователя"""
    if current_user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return current_user


def get_google_accounts_service(db: Session = Depends(get_db)) -> GoogleAccountsService:
    return GoogleAccountsService(db)


def get_google_forms_service_for_account(google_account):
    """Создать GoogleFormsService для конкретного Google аккаунта"""
    if not google_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google аккаунт не найден или токен недоступен",
        )
    
    from app.services.google_forms_service import get_google_forms_service
    return get_google_forms_service(google_account)


# Опциональная авторизация (может быть None)
def get_current_user_optional(
    auth_service: AuthService = Depends(get_auth_service),
    credentials: HTTPAuthorizationCredentials = Depends(optional_security),
) -> User | None:
    """Dependency для получения пользователя (опционально)"""
    if not credentials:
        return None
    try:
        token = credentials.credentials
        user = auth_service.get_current_user(token)
        return user if (user.is_active is True) else None
    except AuthenticationException:
        return None
