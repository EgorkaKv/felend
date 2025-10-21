"""
Google аккаунты пользователя и статус подключения
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_active_user
from app.services.google_accounts_service import GoogleAccountsService
from fastapi import Depends
from app.api.deps import get_google_accounts_service
from app.models import User
from app.schemas import GoogleAccountsListResponse, ErrorResponse
from datetime import datetime, timezone
import logging


router = APIRouter(prefix="/google-accounts", tags=["Google-accounts"])
logger = logging.getLogger(__name__)


@router.get(
    "",
    response_model=GoogleAccountsListResponse,
    responses={
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


@router.post("/{account_id}/set-primary")
async def set_primary_google_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    google_accounts_service: GoogleAccountsService = Depends(
        get_google_accounts_service
    ),
):
    """
    Установить Google аккаунт как основной
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


@router.post("/{account_id}/disconnect")
async def disconnect_google_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    google_accounts_service: GoogleAccountsService = Depends(
        get_google_accounts_service
    ),
):
    """
    Отключить конкретный Google аккаунт
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


@router.get("/google/status")
async def google_connection_status(
    current_user: User = Depends(get_current_active_user),
    google_accounts_service: GoogleAccountsService = Depends(
        get_google_accounts_service
    ),
):
    """
    Проверить статус подключения Google аккаунтов
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
