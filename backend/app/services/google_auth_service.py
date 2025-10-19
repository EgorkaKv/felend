"""
Сервис для работы с Google OAuth 2.0 и Google Forms API
"""

from typing import Dict, Any
import httpx
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.exceptions import GoogleAuthError, RefreshError
from app.core.security import create_oauth_state, verify_oauth_state
from app.repositories.user_repository import user_repository
from app.core.exceptions import GoogleAPIException, FelendException
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
        
    def get_authorization_url(self, user_id: int) -> str:
        """
        Получить URL для авторизации пользователя в Google.

        Возвращаемый URL уже содержит параметр state для защиты от CSRF.
        """

        state = create_oauth_state(user_id)

        flow = Flow.from_client_config(
            self.client_config, scopes=google_settings.GOOGLE_SCOPES
        )
        flow.redirect_uri = google_settings.GOOGLE_REDIRECT_URI

        authorization_url, _ = flow.authorization_url(
            access_type="offline", include_granted_scopes="true", state=state, prompt="consent"
        )

        return authorization_url


    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Обменять authorization code на токены"""
        try:
            # Создаем flow без проверки скопов для избежания проблем с их порядком
            flow = Flow.from_client_config(
                self.client_config, scopes=google_settings.GOOGLE_SCOPES
            )
            flow.redirect_uri = google_settings.GOOGLE_REDIRECT_URI

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
    ):
        """
        Обработка Google OAuth callback: проверка state, обмен code на токены, поиск пользователя, подключение Google аккаунта.
        Возвращает dict с результатом для контроллера.
        """
        # Проверяем и декодируем JWT state
        state_payload = verify_oauth_state(state)
        print(1)
        if not state_payload:
            raise GoogleAPIException("Недействительный или истекший state параметр")
        print(2)
        user_id = state_payload.get("user_id")

        if not user_id:
            raise GoogleAPIException("Отсутствует user_id в state")
        print(3)
        tokens_data = await self.exchange_code_for_tokens(code)
        print(4)
        google_user_info = tokens_data["user_info"]
        google_email = google_user_info.get("email")
        google_name = google_user_info.get("name", "Google User")

        if not google_email:
            raise GoogleAPIException("Не удалось получить email от Google")
        print(5)
        # FIXME: четкие объекты получаемы от гугл, а не пальцем в небо
        google_id = google_user_info.get("sub") or google_user_info.get("id")
        expires_at = None

        if tokens_data.get("expires_at"):
            expires_at = datetime.fromtimestamp(
                tokens_data["expires_at"], tz=timezone.utc
            )

        print(7)
        user = user_repository.get(self.db, user_id)

        if not user:
            raise GoogleAPIException("Пользователь не найден")
        print(8)

        try:
            google_account = google_account_service.connect_google_account(
                user_id=user.id,
                google_id=google_id,
                email=google_email,
                name=google_name,
                access_token=tokens_data["access_token"],
                refresh_token=tokens_data.get("refresh_token"),
                token_expires_at=expires_at,
            )
            print(9)
        except ValueError as connect_error:
            raise GoogleAPIException(
                f"Ошибка валидации при подключении Google аккаунта: {connect_error}"
            )
        except Exception as connect_error:
            raise GoogleAPIException(
                f"Не удалось подключить Google аккаунт: {connect_error}"
            )
        return {
            "message": "Google аккаунт успешно подключен",
            "user_id": user.id,
            "user_email": user.email,
            "google_account_id": google_account.id,
            "google_account_email": google_account.email,
            "is_primary": google_account.is_primary,
            "google_connected": True,
        }
