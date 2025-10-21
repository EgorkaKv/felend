"""
Google OAuth endpoints (login, callback)
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.deps import get_google_accounts_service, get_google_auth_service, get_current_active_user
from app.models import User
from app.core.exceptions import GoogleAPIException

import logging

from app.services.google_auth_service import GoogleAuthService

router = APIRouter(tags=["Authentication"], prefix="/auth")
logger = logging.getLogger(__name__)


@router.get("/google/login")
async def google_login(
    current_user: User = Depends(get_current_active_user),
    google_auth_service: GoogleAuthService=Depends(get_google_auth_service),
):
    """
    Инициировать Google OAuth flow для подключения аккаунта к существующему пользователю
    """
    try:
        authorization_url = google_auth_service.get_authorization_url(current_user.id)

        return {
            "authorization_url": authorization_url,
            "message": "Перейдите по ссылке для авторизации в Google",
            "user_id": current_user.id,
        }

    except GoogleAPIException as e:
        logger.error(f"Ошибка создания Google authorization URL: {e}")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    except Exception as e:
        logger.error(f"Неожиданная ошибка в Google login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при инициализации Google авторизации",
        )


@router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="JWT state with user_id"),
    scope: Optional[str] = Query(None, description="Scopes requested during authorization"),
    google_auth_service=Depends(get_google_auth_service),
    google_accounts_service=Depends(get_google_accounts_service)
):
    """
    Callback endpoint для обработки ответа от Google OAuth
    """

    try:
        result = await google_auth_service.link_google_account(
            code, state, google_accounts_service
        )

        return result

    except GoogleAPIException as e:
        logger.error(f"Google API error in callback: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error in Google callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обработке Google авторизации",
        )
