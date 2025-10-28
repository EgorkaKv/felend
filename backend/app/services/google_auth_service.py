"""
Сервис для работы с Google OAuth 2.0 и Google Forms API
"""

from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
import httpx
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.exceptions import GoogleAuthError, RefreshError
from app.core.security import create_oauth_state, verify_oauth_state, create_google_auth_state, verify_google_auth_state, create_access_token, create_refresh_token
from app.repositories.user_repository import user_repository
from app.repositories.oauth_token_repository import oauth_token_repository
from app.core.exceptions import (
    GoogleAPIException, 
    FelendException, 
    InvalidFrontendOriginException,
    TemporaryTokenNotFoundException,
    TemporaryTokenExpiredException
)
from app.core.config import settings
from datetime import datetime, timezone
import logging
from sqlalchemy.orm import Session
from app.core.google_config import google_settings
from app.services.google_accounts_service import GoogleAccountsService


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
                "redirect_uris": [google_settings.GOOGLE_REDIRECT_URI],
            }
        }
    
    def _is_frontend_origin_allowed(self, origin: str) -> bool:
        """
        Проверить, разрешен ли frontend origin
        
        Сравнивает переданный URL с whitelist разрешенных origins.
        Извлекает схему + хост + порт из URL, игнорируя путь и query параметры.
        
        Args:
            origin: Полный URL (например, "http://localhost:3000/auth/callback")
        
        Returns:
            bool: True если origin в whitelist
            
        Examples:
            >>> _is_frontend_origin_allowed("http://localhost:3000/auth/callback")
            True  # если "http://localhost:3000" в ALLOWED_FRONTEND_ORIGINS
            
            >>> _is_frontend_origin_allowed("http://localhost:3000/some/path?token=123")
            True  # путь и query игнорируются
            
            >>> _is_frontend_origin_allowed("http://evil.com")
            False  # не в whitelist
        """
        try:
            # Парсим переданный URL
            parsed = urlparse(origin)
            
            # Формируем origin (scheme + netloc)
            # netloc включает host:port
            if not parsed.scheme or not parsed.netloc:
                logger.warning(f"Invalid origin format: {origin}")
                return False
            
            # Формируем origin без пути: scheme://netloc
            origin_base = f"{parsed.scheme}://{parsed.netloc}"
            
            # Проверяем наличие в whitelist
            allowed = origin_base in settings.allowed_frontend_origins_list
            
            if not allowed:
                logger.warning(
                    f"Origin not allowed: {origin_base}. "
                    f"Allowed origins: {settings.allowed_frontend_origins_list}"
                )
            
            return allowed
            
        except Exception as e:
            logger.error(f"Error parsing origin {origin}: {e}")
            return False
    
    def init_google_auth(self, frontend_redirect_uri: str) -> str:
        """
        Инициировать Google OAuth flow для публичной авторизации/регистрации
        
        Args:
            frontend_redirect_uri: URL фронтенда для редиректа после авторизации
        
        Returns:
            str: URL для редиректа на Google OAuth
            
        Raises:
            InvalidFrontendOriginException: Если origin не в whitelist
        """
        logger.info(f"Initiating Google auth for frontend: {frontend_redirect_uri}")
        
        # Валидация frontend origin
        if not self._is_frontend_origin_allowed(frontend_redirect_uri):
            raise InvalidFrontendOriginException(frontend_redirect_uri)
        
        # Создаем state с frontend_redirect_uri
        state = create_google_auth_state(frontend_redirect_uri)
        
        # Генерируем URL с минимальными scopes (без Google Forms API)
        authorization_url = self.get_authorization_url(
            state=state,
            redirect_uri=google_settings.GOOGLE_REDIRECT_URI,
            scopes=google_settings.GOOGLE_AUTH_SCOPES
        )
        
        logger.info("Google auth URL generated successfully")
        return authorization_url
        
    def get_authorization_url(
        self, 
        state: str,
        redirect_uri: str = google_settings.GOOGLE_REDIRECT_URI,
        scopes: Optional[List[str]] = None
    ) -> str:
        """
        Получить URL для авторизации пользователя в Google
        
        Args:
            state: JWT state токен (создан через create_oauth_state или create_google_auth_state)
            redirect_uri: URL для callback (по умолчанию из конфига)
            scopes: Список scopes (по умолчанию GOOGLE_SCOPES для Forms)
        
        Returns:
            str: URL для редиректа пользователя на Google OAuth
        """
        if scopes is None:
            scopes = google_settings.GOOGLE_SCOPES

        flow = Flow.from_client_config(
            self.client_config, scopes=scopes
        )
        flow.redirect_uri = redirect_uri

        authorization_url, _ = flow.authorization_url(
            access_type="offline", 
            include_granted_scopes="true", 
            state=state, 
            prompt="consent"
        )

        return authorization_url


    async def exchange_code_for_tokens(
        self, 
        code: str,
        redirect_uri: str = google_settings.GOOGLE_REDIRECT_URI,
        scopes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Обменять authorization code на токены
        
        Args:
            code: Authorization code от Google
            redirect_uri: URL callback (должен совпадать с тем, что был в authorization_url)
            scopes: Список scopes (по умолчанию GOOGLE_SCOPES)
        
        Returns:
            Dict с access_token, refresh_token, expires_at, user_info
        """
        if scopes is None:
            scopes = google_settings.GOOGLE_SCOPES
            
        try:
            # Создаем flow без проверки скопов для избежания проблем с их порядком
            flow = Flow.from_client_config(
                self.client_config, scopes=scopes
            )
            flow.redirect_uri = redirect_uri

            # Отключаем строгую проверку скопов
            import warnings
            import asyncio

            loop = asyncio.get_running_loop()
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                await loop.run_in_executor(None, lambda: flow.fetch_token(code=code))

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
                "expires_at": (
                    credentials.expiry.timestamp() if credentials.expiry else None
                ),
                "user_info": user_info,
            }

        except GoogleAuthError as e:
            logger.error(f"Ошибка обмена кода на токены (Google Auth): {e}")
            raise GoogleAPIException("Ошибка авторизации через Google")
        except FelendException as e:
            raise  # Re-raise FelendException as is
        except Exception as e:
            logger.error(f"Неизвестная ошибка обмена кода на токены: {e}")
            raise GoogleAPIException("Не удалось обменять код на токены")

    async def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Получить информацию о пользователе из Google"""
        try:
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(
                        google_settings.GOOGLE_USERINFO_URL,
                        headers={"Authorization": f"Bearer {access_token}"},
                        timeout=10.0,  # 10 секунд таймаут
                    )
                except httpx.TimeoutException:
                    logger.error(
                        "Таймаут при получении информации о пользователе из Google"
                    )
                    raise GoogleAPIException("Время ожидания ответа от Google истекло")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP ошибка при получении информации о пользователе: {e}")
            raise GoogleAPIException(
                "Ошибка HTTP при получении информации о пользователе"
            )
        except FelendException as e:
            raise  # Re-raise FelendException as is
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
                client_secret=google_settings.GOOGLE_CLIENT_SECRET,
            )
            return {
                "access_token": credentials.token,
                "expires_at": (
                    credentials.expiry.timestamp() if credentials.expiry else None
                ),
                "expires_in": (
                    credentials.expiry.timestamp() if credentials.expiry else None
                ),
            }
        except RefreshError as e:
            logger.error(f"Ошибка обновления токена (RefreshError): {e}")
            raise GoogleAPIException("Ошибка обновления токена доступа")
        except Exception as e:
            logger.error(f"Неизвестная ошибка обновления токена: {e}")
            raise GoogleAPIException("Не удалось обновить токен доступа")

    async def link_google_account(
        self, code: str, state: str, google_account_service: GoogleAccountsService
    ) -> dict:
        """
        Обработка Google OAuth callback: проверка state, обмен code на токены, поиск пользователя, подключение Google аккаунта.
        
        Returns:
            dict с ключами:
                - success (bool): Успешность операции
                - frontend_redirect_uri (str | None): URL для редиректа
                - email (str | None): Email Google аккаунта при успехе
                - error_code (str | None): Код ошибки при неудаче
                - error_message (str | None): Сообщение об ошибке при неудаче
        """
        from app.core.exceptions import (
            GoogleAccountAlreadyConnectedException,
            GoogleAccountConnectedToAnotherUserException
        )
        
        # Проверяем и декодируем JWT state
        state_payload = verify_oauth_state(state)
        
        if not state_payload:
            return {
                "success": False,
                "frontend_redirect_uri": None,
                "error_code": "invalid_state",
                "error_message": "Invalid or expired state parameter"
            }
        
        user_id = state_payload.get("user_id")
        frontend_redirect_uri = state_payload.get("frontend_redirect_uri")

        if not user_id:
            return {
                "success": False,
                "frontend_redirect_uri": frontend_redirect_uri,
                "error_code": "invalid_state",
                "error_message": "Missing user_id in state"
            }
        
        try:
            tokens_data = await self.exchange_code_for_tokens(code)
            
            google_user_info = tokens_data["user_info"]
            google_email = google_user_info.get("email")
            google_name = google_user_info.get("name", "Google User")

            if not google_email:
                return {
                    "success": False,
                    "frontend_redirect_uri": frontend_redirect_uri,
                    "error_code": "google_api_error",
                    "error_message": "Failed to retrieve email from Google"
                }
            
            # Извлекаем Google ID
            google_id = google_user_info.get("sub") or google_user_info.get("id")
            expires_at = None

            if tokens_data.get("expires_at"):
                expires_at = datetime.fromtimestamp(
                    tokens_data["expires_at"], tz=timezone.utc
                )

            user = user_repository.get(self.db, user_id)

            if not user:
                return {
                    "success": False,
                    "frontend_redirect_uri": frontend_redirect_uri,
                    "error_code": "user_not_found",
                    "error_message": "User not found"
                }

            # Пытаемся подключить Google аккаунт
            google_account = google_account_service.connect_google_account(
                user_id=user.id,
                google_id=google_id,
                email=google_email,
                name=google_name,
                access_token=tokens_data["access_token"],
                refresh_token=tokens_data.get("refresh_token"),
                token_expires_at=expires_at,
            )
            
            logger.info(f"Google account {google_id} linked to user {user.id}")
            
            return {
                "success": True,
                "frontend_redirect_uri": frontend_redirect_uri,
                "email": google_email
            }
            
        except GoogleAccountAlreadyConnectedException as e:
            return {
                "success": False,
                "frontend_redirect_uri": frontend_redirect_uri,
                "error_code": "account_already_connected",
                "error_message": "This Google account is already connected to your account"
            }
            
        except GoogleAccountConnectedToAnotherUserException as e:
            return {
                "success": False,
                "frontend_redirect_uri": frontend_redirect_uri,
                "error_code": "account_connected_to_another_user",
                "error_message": "This Google account is already connected to another user"
            }
            
        except GoogleAPIException as e:
            return {
                "success": False,
                "frontend_redirect_uri": frontend_redirect_uri,
                "error_code": "google_api_error",
                "error_message": str(e.message) if hasattr(e, 'message') else str(e)
            }
            
        except Exception as e:
            logger.error(f"Unexpected error linking Google account: {e}")
            return {
                "success": False,
                "frontend_redirect_uri": frontend_redirect_uri,
                "error_code": "internal_error",
                "error_message": "An unexpected error occurred"
            }
    
    async def process_google_auth_callback(
        self, 
        code: str, 
        state: str,
        google_accounts_service: GoogleAccountsService
    ) -> Tuple[str, str]:
        """
        Обработка Google OAuth callback для публичной авторизации/регистрации
        
        Args:
            code: Authorization code от Google
            state: JWT state с frontend_redirect_uri
            google_accounts_service: Сервис для работы с Google аккаунтами
        
        Returns:
            Tuple[temporary_token, frontend_redirect_uri]: Одноразовый токен и URL для редиректа
            
        Raises:
            GoogleAPIException: Ошибки при работе с Google API
            InvalidFrontendOriginException: Некорректный state
        """
        # Cleanup expired tokens
        oauth_token_repository.cleanup_expired(self.db)
        
        # Проверяем и декодируем JWT state
        state_payload = verify_google_auth_state(state)
        if not state_payload:
            raise GoogleAPIException("Недействительный или истекший state параметр")
        
        frontend_redirect_uri = state_payload.get("frontend_redirect_uri")
        if not frontend_redirect_uri:
            raise GoogleAPIException("Отсутствует frontend_redirect_uri в state")
        
        # Обмениваем code на токены Google (с минимальными scopes)
        tokens_data = await self.exchange_code_for_tokens(
            code=code,
            redirect_uri=google_settings.GOOGLE_REDIRECT_URI,
            scopes=google_settings.GOOGLE_AUTH_SCOPES
        )
        
        google_user_info = tokens_data["user_info"]
        google_id = google_user_info.get("sub") or google_user_info.get("id")
        google_email = google_user_info.get("email")
        google_name = google_user_info.get("name", "Google User")
        
        if not google_email or not google_id:
            raise GoogleAPIException("Не удалось получить email или ID от Google")
        
        # Регистрируем или авторизуем пользователя
        expires_at = None
        if tokens_data.get("expires_at"):
            expires_at = datetime.fromtimestamp(tokens_data["expires_at"], tz=timezone.utc)
        
        user, google_account = google_accounts_service.register_or_login_google_user(
            google_id=google_id,
            email=google_email,
            full_name=google_name,
            access_token=tokens_data["access_token"],
            refresh_token=tokens_data.get("refresh_token"),
            token_expires_at=expires_at
        )
        
        # Создаем одноразовый токен (TTL 5 минут)
        temporary_token = oauth_token_repository.create_token(
            db=self.db,
            user_id=user.id,
            ttl_minutes=5
        )
        
        return temporary_token, frontend_redirect_uri
    
    def exchange_temporary_token(self, token: str) -> Tuple[str, str, dict]:
        """
        Обменять одноразовый токен на JWT access/refresh tokens
        
        Args:
            token: Одноразовый токен из callback
        
        Returns:
            Tuple[access_token, refresh_token, user_dict]: JWT токены и данные пользователя
            
        Raises:
            TemporaryTokenNotFoundException: Токен не найден
            TemporaryTokenExpiredException: Токен истек или уже использован
        """
        # Cleanup expired tokens
        oauth_token_repository.cleanup_expired(self.db)
        
        # Получаем токен из БД
        oauth_token = oauth_token_repository.get_by_token(self.db, token)
        
        if not oauth_token:
            raise TemporaryTokenNotFoundException(token)
        
        # Проверяем валидность токена
        if not oauth_token_repository.is_token_valid(oauth_token):
            raise TemporaryTokenExpiredException(token)
        
        # Помечаем токен как использованный
        oauth_token_repository.mark_as_used(self.db, oauth_token.id)
        
        # Получаем пользователя
        user = user_repository.get(self.db, oauth_token.user_id)
        
        if not user:
            raise GoogleAPIException("Пользователь не найден")
        
        # Создаем JWT токены
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        # Формируем данные пользователя
        user_dict = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "balance": user.balance,
            "respondent_code": user.respondent_code,
            "created_at": user.created_at
        }
        
        return access_token, refresh_token, user_dict
