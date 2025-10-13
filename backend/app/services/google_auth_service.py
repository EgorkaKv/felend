"""
Сервис для работы с Google OAuth 2.0 и Google Forms API
"""

from typing import Dict, Any, Optional
from fastapi import Depends
import httpx
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from app.api.deps import get_auth_service, get_google_accounts_service
from app.core.security import create_oauth_state, verify_oauth_state
from app.repositories.user_repository import user_repository
from app.core.exceptions import GoogleAPIException
from datetime import datetime, timezone
import logging
from sqlalchemy.orm import Session
from app.core.google_config import google_settings
from app.core.exceptions import GoogleAPIException


logger = logging.getLogger(__name__)


class GoogleAuthService:
    """Сервис для работы с Google OAuth 2.0"""
    
    def __init__(self, db: Session):
        self.db = db
        self.client_config = {
            "web": {
                "client_id": google_settings.GOOGLE_CLIENT_ID,
                "client_secret": google_settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": google_settings.GOOGLE_AUTH_URL,
                "token_uri": google_settings.GOOGLE_TOKEN_URL,
                "redirect_uris": [google_settings.GOOGLE_REDIRECT_URI]
            }
        }
    
    def get_authorization_url(self, user_id: int) -> str:
        """Получить URL для авторизации пользователя в Google"""
        try:
            state = create_oauth_state(user_id)
            
            flow = Flow.from_client_config(
                self.client_config,
                scopes=google_settings.GOOGLE_SCOPES
            )
            flow.redirect_uri = google_settings.GOOGLE_REDIRECT_URI
            
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state
            )
            
            return authorization_url
        
        except Exception as e:
            logger.error(f"Ошибка создания URL авторизации: {e}")
            raise GoogleAPIException("Не удалось создать URL авторизации")


    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Обменять authorization code на токены"""
        try:
            # Создаем flow без проверки скопов для избежания проблем с их порядком
            flow = Flow.from_client_config(
                self.client_config,
                scopes=google_settings.GOOGLE_SCOPES
            )
            flow.redirect_uri = google_settings.GOOGLE_REDIRECT_URI
            

            # Отключаем строгую проверку скопов
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                flow.fetch_token(code=code)
            
            credentials = flow.credentials

            if not credentials or not credentials.token:
                raise GoogleAPIException("Не удалось получить токены доступа")
            
            # Логируем полученные скопы для отладки
            logger.info(f"Получены скопы: {credentials.scopes}")
            
            # Получить информацию о пользователе
            user_info = await self._get_user_info(credentials.token)
            
            return {
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "expires_in": credentials.expiry.timestamp() if credentials.expiry else None,
                "user_info": user_info
            }
        
        except Exception as e:
            logger.error(f"Ошибка обмена кода на токены: {e}")
            raise GoogleAPIException("Не удалось получить токены доступа")


    async def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Получить информацию о пользователе из Google"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    google_settings.GOOGLE_USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Ошибка получения информации о пользователе: {e}")
            raise GoogleAPIException("Не удалось получить информацию о пользователе")


    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Обновить access token используя refresh token"""
        try:
            credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri=google_settings.GOOGLE_TOKEN_URL,
                client_id=google_settings.GOOGLE_CLIENT_ID,
                client_secret=google_settings.GOOGLE_CLIENT_SECRET
            )
            
            credentials.refresh(Request())
            
            return {
                "access_token": credentials.token,
                "expires_in": credentials.expiry.timestamp() if credentials.expiry else None
            }
        except Exception as e:
            logger.error(f"Ошибка обновления токена: {e}")
            raise GoogleAPIException("Не удалось обновить токен доступа")


    async def link_google_account(
        self, code: str, state: str, 
        google_account_service = Depends(get_google_accounts_service)
        ):
        """
        Обработка Google OAuth callback: проверка state, обмен code на токены, поиск пользователя, подключение Google аккаунта.
        Возвращает dict с результатом для контроллера.
        """
       
        # Проверяем и декодируем JWT state
        state_payload = verify_oauth_state(state)

        if not state_payload:
            raise GoogleAPIException("Недействительный или истекший state параметр")
        
        user_id = state_payload.get("user_id")
        
        if not user_id:
            raise GoogleAPIException("Отсутствует user_id в state")
        
        tokens_data = await self.exchange_code_for_tokens(code)
        
        google_user_info = tokens_data["user_info"]
        google_email = google_user_info.get("email")
        google_name = google_user_info.get("name", "Google User")
        
        if not google_email:
            raise GoogleAPIException("Не удалось получить email от Google")
        
        # FIXME: четкие объекты получаемы от гугл, а не пальцем в небо
        google_id = google_user_info.get("sub") or google_user_info.get("id")
        
        if not google_id:
            raise GoogleAPIException("Не удалось получить Google ID")
        
        expires_at = None
        
        if tokens_data.get("expires_in"):
            expires_at = datetime.fromtimestamp(tokens_data["expires_in"], tz=timezone.utc)
        
        user = user_repository.get(self.db, user_id)
        
        if not user:
            raise GoogleAPIException("Пользователь не найден")
        
        
        try:
            google_account = google_account_service.connect_google_account(
                user_id=user.id,
                google_id=google_id,
                email=google_email,
                name=google_name,
                access_token=tokens_data["access_token"],
                refresh_token=tokens_data.get("refresh_token"),
                token_expires_at=expires_at
            )
        except Exception as connect_error:
            raise GoogleAPIException(f"Не удалось подключить Google аккаунт: {connect_error}")
        return {
            "message": "Google аккаунт успешно подключен",
            "user_id": user.id,
            "user_email": user.email,
            "google_account_id": google_account.id,
            "google_account_email": google_account.email,
            "is_primary": google_account.is_primary,
            "google_connected": True
        }
