"""
Google OAuth endpoints для публичной авторизации/регистрации
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import RedirectResponse
from app.api.deps import get_google_accounts_service, get_google_auth_service, get_db
from app.schemas import GoogleAuthInitRequest, GoogleAuthInitResponse, ExchangeTokenRequest, ExchangeTokenResponse, UserProfile, ErrorResponse
from sqlalchemy.orm import Session
import logging

from app.services.google_auth_service import GoogleAuthService
from app.services.google_accounts_service import GoogleAccountsService

router = APIRouter(tags=["Authentication"], prefix="/auth")
logger = logging.getLogger(__name__)


@router.post(
    "/google/login",
    response_model=GoogleAuthInitResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        422: {"model": ErrorResponse, "description": "Frontend origin not allowed"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def google_login(
    request: GoogleAuthInitRequest,
    google_auth_service: GoogleAuthService = Depends(get_google_auth_service),
):
    """
    Инициировать Google OAuth flow для регистрации/входа (публичный endpoint)
    
    Возвращает URL для авторизации Google. Frontend должен редиректить пользователя
    на этот URL через window.location.href (не через fetch/axios).
    После успешной авторизации Google редиректит на /auth/google/callback.
    """
    authorization_url = google_auth_service.init_google_auth(
        str(request.frontend_redirect_uri)
    )
    
    return GoogleAuthInitResponse(
        authorization_url=authorization_url,  # type: ignore
        message="Redirect to Google for authentication"
    )


@router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="JWT state with frontend_redirect_uri"),
    google_auth_service: GoogleAuthService = Depends(get_google_auth_service),
    google_accounts_service: GoogleAccountsService = Depends(get_google_accounts_service),
):
    """
    Callback endpoint для Google OAuth (регистрация/вход)
    
    1. Проверяет state
    2. Обменивает code на токены Google
    3. Регистрирует или авторизует пользователя
    4. Создает одноразовый токен
    5. Редиректит на frontend с токеном
    """
    temporary_token, frontend_redirect_uri = await google_auth_service.process_google_auth_callback(
        code=code,
        state=state,
        google_accounts_service=google_accounts_service
    )
    
    # Редиректим на frontend с токеном
    redirect_url = f"{frontend_redirect_uri}?token={temporary_token}"
    
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.post(
    "/google/exchange-token",
    response_model=ExchangeTokenResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid or expired token"},
        404: {"model": ErrorResponse, "description": "Token not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def exchange_token(
    request: ExchangeTokenRequest,
    google_auth_service: GoogleAuthService = Depends(get_google_auth_service),
):
    """
    Обменять одноразовый токен на JWT access/refresh tokens
    
    Frontend вызывает этот endpoint после редиректа с /auth/google/callback.
    Токен действителен 5 минут и может быть использован только один раз.
    """
    access_token, refresh_token, user_dict = google_auth_service.exchange_temporary_token(
        request.token
    )
    
    # Формируем ответ
    user_profile = UserProfile(**user_dict)
    
    return ExchangeTokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=1800,  # 30 minutes
        user=user_profile
    )

