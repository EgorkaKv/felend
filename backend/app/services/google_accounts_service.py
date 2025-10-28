from typing import Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import User, BalanceTransaction, TransactionType, GoogleAccount
from app.repositories.user_repository import user_repository
from app.repositories.google_account_repository import google_account_repository
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.exceptions import UserAlreadyExistsException, AuthorizationException
from app.core.config import settings


class GoogleAccountsService:
    def __init__(self, db: Session):
        self.user_repo = user_repository
        self.google_account_repo = google_account_repository
        self.db = db

    def connect_google_account(
        self,
        user_id: int,
        google_id: str,
        email: str,
        name: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        token_expires_at: Optional[datetime] = None,
    ) -> GoogleAccount:
        """
        Подключить Google аккаунт к существующему пользователю
        
        Raises:
            GoogleAccountAlreadyConnectedException: Если аккаунт уже подключен к этому пользователю
            GoogleAccountConnectedToAnotherUserException: Если аккаунт подключен к другому пользователю
        """
        from app.core.exceptions import (
            GoogleAccountAlreadyConnectedException,
            GoogleAccountConnectedToAnotherUserException
        )
        
        existing_google_account = self.google_account_repo.get_by_google_id(
            self.db, google_id
        )

        if existing_google_account:
            # Проверяем, к какому пользователю привязан аккаунт
            if existing_google_account.user_id == user_id:
                # Аккаунт уже подключен к текущему пользователю
                raise GoogleAccountAlreadyConnectedException(
                    google_email=email,
                    context={"google_id": google_id, "user_id": user_id}
                )
            else:
                # Аккаунт подключен к другому пользователю
                raise GoogleAccountConnectedToAnotherUserException(
                    google_email=email,
                    context={"google_id": google_id}
                )

        return self.google_account_repo.create_google_account(
            db=self.db,
            user_id=user_id,
            google_id=google_id,
            email=email,
            name=name,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=token_expires_at,
        )

    def register_or_login_google_user(
        self,
        google_id: str,
        email: str,
        full_name: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        token_expires_at: Optional[datetime] = None,
    ) -> Tuple[User, GoogleAccount]:
        """
        Регистрация или вход через Google OAuth (возвращает пользователя и Google аккаунт)
        
        Логика поиска (согласно google-auth-flow.md):
        1. Ищем в google_accounts по google_id → если нашли → авторизация (обновляем токены)
        2. Ищем в users по email → если нашли → авторизация + привязка Google аккаунта
        3. Если не нашли → регистрация нового пользователя + создание Google аккаунта
        """
        # Шаг 1: Ищем существующий Google аккаунт по google_id
        existing_google_account = self.google_account_repo.get_by_google_id(
            self.db, google_id
        )

        if existing_google_account:
            # Google аккаунт уже привязан к пользователю → авторизация
            google_account = self.google_account_repo.update_tokens(
                db=self.db,
                account_id=existing_google_account.id,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=token_expires_at,
            )

            user = self.user_repo.get(self.db, existing_google_account.user_id)
            return user, google_account
        
        # Шаг 2: Google аккаунт не найден, ищем пользователя по email
        existing_user = self.user_repo.get_by_email(self.db, email)
        if existing_user:
            # Пользователь существует (регистрировался через email+password)
            # → авторизация + привязка Google аккаунта
            google_account = self.google_account_repo.create_google_account(
                db=self.db,
                user_id=existing_user.id,
                google_id=google_id,
                email=email,
                name=full_name,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=token_expires_at,
            )
            return existing_user, google_account
        
        # Шаг 3: Пользователь не найден → регистрация нового пользователя
        else:
            user = self.user_repo.create_user(
                db=self.db,
                email=email,
                full_name=full_name,
                password=None,  # Google пользователи без пароля
            )

            welcome_transaction = BalanceTransaction(
                user_id=user.id,
                transaction_type=TransactionType.BONUS,
                amount=settings.WELCOME_BONUS_POINTS,
                balance_after=user.balance,
                description="Welcome bonus for new Google user",
            )

            self.db.add(welcome_transaction)
            self.db.commit()
            
            google_account = self.google_account_repo.create_google_account(
                db=self.db,
                user_id=user.id,
                google_id=google_id,
                email=email,
                name=full_name,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=token_expires_at,
            )
            return user, google_account

    def get_user_google_accounts(self, user_id: int) -> list[GoogleAccount]:
        """Получить все Google аккаунты пользователя"""
        return self.google_account_repo.get_by_user_id(self.db, user_id)

    def check_user_google_account(
        self, user_id: int, account_id: int
    ) -> Optional[GoogleAccount]:
        """Проверить принадлежность Google аккаунта пользователю"""
        
        account: Optional[GoogleAccount] = self.google_account_repo.get_by_id(self.db, account_id)
        if not account or account.user_id != user_id:
            raise AuthorizationException("Google account does not belong to user")

        if self.google_account_repo.account_have_tokens(self.db, account_id):
            return account
        return None

    def get_primary_google_account(self, user_id: int) -> Optional[GoogleAccount]:
        """Получить основной Google аккаунт пользователя"""
        return self.google_account_repo.get_primary_for_user(self.db, user_id)

    def set_primary_google_account(
        self, user_id: int, account_id: int
    ) -> GoogleAccount:
        """Установить основной Google аккаунт"""
        return self.google_account_repo.set_primary(self.db, account_id, user_id)

    def disconnect_google_account(self, user_id: int, account_id: int) -> bool:
        """Отключить Google аккаунт"""
        return self.google_account_repo.deactivate(self.db, account_id, user_id)
