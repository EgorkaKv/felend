"""
Google аккаунты пользователя и статус подключения
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Query
from fastapi.responses import RedirectResponse
from app.api.deps import get_current_active_user, get_google_auth_service
from app.core.exceptions import GoogleAPIException, InvalidFrontendOriginException
from app.core.security import create_oauth_state
from app.services.google_accounts_service import GoogleAccountsService
from fastapi import Depends
from app.api.deps import get_google_accounts_service
from app.models import User
from app.schemas import GoogleAccountsListResponse, ErrorResponse
from datetime import datetime, timezone
import logging
from urllib.parse import urlencode

from app.services.google_auth_service import GoogleAuthService


router = APIRouter(prefix="/google-accounts", tags=["Google-accounts"])
logger = logging.getLogger(__name__)

@router.get(
    "/connect",
    summary="Initiate Google OAuth for account linking",
    description="Initiate Google OAuth flow to link a Google account to the authenticated user for Google Forms access",
    responses={
        200: {
            "description": "Authorization URL generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "authorization_url": "https://accounts.google.com/o/oauth2/auth?...",
                        "message": "Перейдите по ссылке для авторизации в Google",
                        "user_id": 1
                    }
                }
            }
        },
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        422: {"model": ErrorResponse, "description": "Frontend origin not allowed"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        502: {"model": ErrorResponse, "description": "Google API error"}
    }
)
async def google_connect(
    redirect_uri: str = Query(..., description="Frontend URL for redirect after OAuth completion"),
    current_user: User = Depends(get_current_active_user),
    google_auth_service: GoogleAuthService=Depends(get_google_auth_service),
):
    """
    Инициировать Google OAuth flow для подключения аккаунта к существующему пользователю (для Google Forms)
    
    Frontend должен передать redirect_uri, на который будет выполнен редирект после обработки callback.
    После успешной авторизации пользователь будет перенаправлен на redirect_uri с параметрами:
    - Success: ?google_connected=success&email=student@gmail.com
    - Error: ?google_connected=error&error_code=account_already_connected&message=...
    
    Frontend должен перенаправить пользователя на authorization_url используя window.location.href.
    """
    try:
        # Валидируем frontend origin
        if not google_auth_service._is_frontend_origin_allowed(redirect_uri):
            raise InvalidFrontendOriginException(redirect_uri)
        
        # Создаем state с user_id и frontend_redirect_uri
        state = create_oauth_state(
            user_id=current_user.id,
            frontend_redirect_uri=redirect_uri
        )
        
        # Генерируем URL с полными scopes (включая Google Forms API)
        authorization_url = google_auth_service.get_authorization_url(
            state=state,
            redirect_uri="http://127.0.0.1:8000/api/v1/google-accounts/callback"
        )

        return {
            "authorization_url": authorization_url,
            "message": "Перейдите по ссылке для авторизации в Google",
            "user_id": current_user.id,
        }

    except InvalidFrontendOriginException:
        raise
    
    except GoogleAPIException as e:
        logger.error(f"Ошибка создания Google authorization URL: {e}")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    except Exception as e:
        logger.error(f"Неожиданная ошибка в Google connect: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при инициализации Google авторизации",
        )


@router.get(
    "/callback",
    summary="Google OAuth callback for account linking",
    description="Handles the OAuth callback from Google, exchanges authorization code for tokens, and links the Google account to the user. Redirects to frontend with success or error parameters.",
    responses={
        302: {"description": "Redirect to frontend with success or error parameters"},
        500: {"description": "Internal server error without redirect_uri"}
    }
)
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="JWT state with user_id and frontend_redirect_uri"),
    scope: Optional[str] = Query(None, description="Scopes requested during authorization"),
    google_auth_service=Depends(get_google_auth_service),
    google_accounts_service=Depends(get_google_accounts_service)
):
    """
    Callback endpoint для обработки ответа от Google OAuth
    
    Автоматически вызывается Google после успешной авторизации.
    Обменивает authorization code на токены, привязывает Google аккаунт к пользователю,
    и делает редирект на frontend с параметрами результата:
    
    Success: ?google_connected=success&email=student@gmail.com
    Error: ?google_connected=error&error_code=account_already_connected&message=...
    """
    try:
        result = await google_auth_service.link_google_account(
            code, state, google_accounts_service
        )
        
        frontend_redirect_uri = result.get("frontend_redirect_uri")
        
        # Если нет frontend_redirect_uri (например, при ошибке парсинга state), возвращаем ошибку
        if not frontend_redirect_uri:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process callback: missing redirect URI"
            )
        
        # Формируем query параметры для редиректа
        if result["success"]:
            params = {
                "google_connected": "success",
                "email": result["email"]
            }
        else:
            params = {
                "google_connected": "error",
                "error_code": result["error_code"],
                "message": result["error_message"]
            }
        
        # Создаем URL с параметрами
        redirect_url = f"{frontend_redirect_uri}?{urlencode(params)}"
        logger.info(f"Redirecting to: {redirect_url}")
        
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

    except Exception as e:
        logger.error(f"Unexpected error in Google callback: {e}")
        # Если произошла критическая ошибка и нет redirect_uri, возвращаем HTTP error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process Google OAuth callback",
        )


@router.get(
    "",
    response_model=GoogleAccountsListResponse,
    summary="List all linked Google accounts",
    description="Get a list of all Google accounts linked to the authenticated user",
    responses={
        200: {
            "description": "List of Google accounts retrieved successfully",
            "model": GoogleAccountsListResponse
        },
        401: {"model": ErrorResponse, "description": "Authentication required"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def list_google_accounts(
    current_user: User = Depends(get_current_active_user),
    google_accounts_service: GoogleAccountsService = Depends(
        get_google_accounts_service
    ),
):
    """
    Get list of all user's Google accounts
    
    Returns all Google accounts that the user has connected for Google Forms access.
    Each account includes its email, name, primary status, and connection status.
    """
    try:
        google_accounts = google_accounts_service.get_user_google_accounts(
            current_user.id
        )
        accounts_data = []
        for account in google_accounts:
            from app.schemas import GoogleAccountDetail
            accounts_data.append(
                GoogleAccountDetail(
                    id=account.id,
                    email=account.email,
                    name=account.name,
                    is_primary=account.is_primary,
                    is_active=account.is_active,
                    created_at=account.created_at,
                )
            )
        return GoogleAccountsListResponse(
            google_accounts=accounts_data, 
            total_accounts=len(accounts_data)
        )
    except Exception as e:
        logger.error(f"Error listing Google accounts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving Google accounts",
        )


@router.post(
    "/{account_id}/set-primary",
    summary="Set Google account as primary",
    description="Set a specific Google account as the primary account for the authenticated user. The primary account is used by default for Google Forms operations.",
    responses={
        200: {
            "description": "Primary account set successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Основной Google аккаунт изменен",
                        "primary_account": {
                            "id": 5,
                            "email": "student@gmail.com",
                            "name": "John Doe"
                        }
                    }
                }
            }
        },
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Google account not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def set_primary_google_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    google_accounts_service: GoogleAccountsService = Depends(
        get_google_accounts_service
    ),
):
    """
    Установить Google аккаунт как основной
    
    Основной аккаунт используется по умолчанию для всех операций с Google Forms.
    Только один аккаунт может быть основным в каждый момент времени.
    """
    try:
        google_account = google_accounts_service.set_primary_google_account(
            current_user.id, account_id
        )
        if not google_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Google аккаунт не найден"
            )
        return {
            "message": "Основной Google аккаунт изменен",
            "primary_account": {
                "id": google_account.id,
                "email": google_account.email,
                "name": google_account.name,
            },
        }

    except Exception as e:
        logger.error(f"Error setting primary Google account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при установке основного аккаунта",
        )


@router.post(
    "/{account_id}/disconnect",
    summary="Disconnect Google account",
    description="Disconnect and remove a specific Google account from the authenticated user. This will revoke access to Google Forms for this account.",
    responses={
        200: {
            "description": "Google account disconnected successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Google аккаунт отключен",
                        "disconnected_account_id": 5
                    }
                }
            }
        },
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Google account not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def disconnect_google_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    google_accounts_service: GoogleAccountsService = Depends(
        get_google_accounts_service
    ),
):
    """
    Отключить конкретный Google аккаунт
    
    Удаляет связь между пользователем и Google аккаунтом.
    После отключения доступ к Google Forms через этот аккаунт будет невозможен.
    """
    try:
        success = google_accounts_service.disconnect_google_account(
            current_user.id, account_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Google аккаунт не найден"
            )
        return {
            "message": "Google аккаунт отключен",
            "disconnected_account_id": account_id,
        }
    except Exception as e:
        logger.error(f"Error disconnecting Google account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при отключении Google аккаунта",
        )


def is_token_valid(token_expires_at):
    """
    Проверяет, действителен ли токен (не истек ли срок действия)
    """
    if not token_expires_at:
        return False
    # If token_expires_at is naive (no tzinfo), assume it's in UTC to avoid
    # comparing offset-naive and offset-aware datetimes.
    if token_expires_at.tzinfo is None or token_expires_at.tzinfo.utcoffset(token_expires_at) is None:
        token_expires_at = token_expires_at.replace(tzinfo=timezone.utc)
    return token_expires_at > datetime.now(timezone.utc)


@router.get(
    "/google/status",
    summary="Check Google account connection status",
    description="Get the current Google account connection status including total accounts, primary account details, and token validity",
    responses={
        200: {
            "description": "Google connection status retrieved successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "with_accounts": {
                            "summary": "User has Google accounts connected",
                            "value": {
                                "google_connected": True,
                                "total_accounts": 2,
                                "primary_account": {
                                    "id": 5,
                                    "email": "student@gmail.com",
                                    "name": "John Doe",
                                    "token_valid": True,
                                    "expires_at": "2025-11-29T12:00:00Z"
                                }
                            }
                        },
                        "without_accounts": {
                            "summary": "User has no Google accounts",
                            "value": {
                                "google_connected": False,
                                "total_accounts": 0,
                                "primary_account": None
                            }
                        }
                    }
                }
            }
        },
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def google_connection_status(
    current_user: User = Depends(get_current_active_user),
    google_accounts_service: GoogleAccountsService = Depends(
        get_google_accounts_service
    ),
):
    """
    Проверить статус подключения Google аккаунтов
    
    Возвращает информацию о подключенных Google аккаунтах:
    - Общее количество подключенных аккаунтов
    - Информацию о основном аккаунте
    - Валидность токенов (срок действия)
    """
    try:
        google_accounts = google_accounts_service.get_user_google_accounts(
            current_user.id
        )
        primary_account = google_accounts_service.get_primary_google_account(
            current_user.id
        )
        has_google_accounts = len(google_accounts) > 0
        primary_token_valid = is_token_valid(primary_account.token_expires_at) if primary_account else False
        return {
            "google_connected": has_google_accounts,
            "total_accounts": len(google_accounts),
            "primary_account": (
                {
                    "id": primary_account.id,
                    "email": primary_account.email,
                    "name": primary_account.name,
                    "token_valid": primary_token_valid,
                    "expires_at": (
                        primary_account.token_expires_at.isoformat()
                        if primary_account.token_expires_at
                        else None
                    ),
                }
                if primary_account
                else None
            ),
        }
    except Exception as e:
        logger.error(f"Error getting Google status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при проверке статуса Google подключения",
        )
