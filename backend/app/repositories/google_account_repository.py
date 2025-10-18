"""
Репозиторий для работы с Google аккаунтами
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import GoogleAccount, User
from app.repositories.base_repository import BaseRepository
from app.schemas import GoogleAccountCreate, GoogleAccountUpdate


class GoogleAccountRepository(
    BaseRepository[GoogleAccount, GoogleAccountCreate, GoogleAccountUpdate]
):
    """Репозиторий для работы с Google аккаунтами"""

    def __init__(self):
        super().__init__(GoogleAccount)

    def get_by_user_id(self, db: Session, user_id: int) -> List[GoogleAccount]:
        """Получить все Google аккаунты пользователя"""
        return (
            db.query(GoogleAccount)
            .filter(GoogleAccount.user_id == user_id, GoogleAccount.is_active == True)
            .all()
        )

    def get_by_google_id(self, db: Session, google_id: str) -> Optional[GoogleAccount]:
        """Получить Google аккаунт по Google ID"""
        return (
            db.query(GoogleAccount)
            .filter(
                GoogleAccount.google_id == google_id, GoogleAccount.is_active == True
            )
            .first()
        )

    def get_by_email(self, db: Session, email: str) -> Optional[GoogleAccount]:
        """Получить Google аккаунт по email"""
        return (
            db.query(GoogleAccount)
            .filter(GoogleAccount.email == email, GoogleAccount.is_active == True)
            .first()
        )

    def get_by_id(self, db: Session, id: int) -> Optional[GoogleAccount]:
        """Получить Google аккаунт по ID"""
        return (
            db.query(GoogleAccount)
            .filter(GoogleAccount.id == id, GoogleAccount.is_active == True)
            .first()
        )
    
    def account_have_tokens(self, db: Session, id: int) -> bool:
        """Проверить, есть ли у аккаунта токены"""
        account = (
            db.query(GoogleAccount)
            .filter(GoogleAccount.id == id, GoogleAccount.is_active == True)
            .first()
        )
        if account and (account.access_token or account.refresh_token):
            return True
        return False

    def get_primary_for_user(
        self, db: Session, user_id: int
    ) -> Optional[GoogleAccount]:
        """Получить основной Google аккаунт пользователя"""
        return (
            db.query(GoogleAccount)
            .filter(
                GoogleAccount.user_id == user_id,
                GoogleAccount.is_primary == True,
                GoogleAccount.is_active == True,
            )
            .first()
        )

    def set_primary(self, db: Session, account_id: int, user_id: int) -> GoogleAccount:
        """Установить Google аккаунт как основной для пользователя"""
        # Снимаем флаг primary со всех аккаунтов пользователя
        db.query(GoogleAccount).filter(
            GoogleAccount.user_id == user_id, GoogleAccount.is_active == True
        ).update({"is_primary": False})

        # Устанавливаем флаг primary для выбранного аккаунта
        account = (
            db.query(GoogleAccount)
            .filter(
                GoogleAccount.id == account_id,
                GoogleAccount.user_id == user_id,
                GoogleAccount.is_active == True,
            )
            .first()
        )

        if account:
            account.is_primary = True
            db.commit()
            db.refresh(account)

        return account

    def create_google_account(
        self,
        db: Session,
        user_id: int,
        google_id: str,
        email: str,
        name: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        token_expires_at=None,
        is_primary: bool = False,
    ) -> GoogleAccount:
        """Создать новый Google аккаунт"""
        # FIXME: убрать бизнес-логику из репозитория
        # Если это первый Google аккаунт пользователя, делаем его основным
        existing_accounts = self.get_by_user_id(db, user_id)
        if not existing_accounts:
            is_primary = True

        google_account = GoogleAccount(
            user_id=user_id,
            google_id=google_id,
            email=email,
            name=name,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=token_expires_at,
            is_primary=is_primary,
            is_active=True,
        )

        db.add(google_account)
        db.commit()
        db.refresh(google_account)

        return google_account

    def update_tokens(
        self,
        db: Session,
        account_id: int,
        access_token: str,
        refresh_token: Optional[str] = None,
        token_expires_at=None,
    ) -> Optional[GoogleAccount]:
        """Обновить токены Google аккаунта"""
        account = (
            db.query(GoogleAccount)
            .filter(GoogleAccount.id == account_id, GoogleAccount.is_active == True)
            .first()
        )

        if account:
            account.access_token = access_token
            if refresh_token:
                account.refresh_token = refresh_token
            if token_expires_at:
                account.token_expires_at = token_expires_at

            db.commit()
            db.refresh(account)

        return account

    def deactivate(self, db: Session, account_id: int, user_id: int) -> bool:
        """Деактивировать Google аккаунт"""
        account = (
            db.query(GoogleAccount)
            .filter(
                GoogleAccount.id == account_id,
                GoogleAccount.user_id == user_id,
                GoogleAccount.is_active == True,
            )
            .first()
        )

        # FIXME: убрать бизнес-логику из репозитория
        if account:
            account.is_active = False
            # Если это был основной аккаунт, назначаем другой основным
            if account.is_primary:
                account.is_primary = False
                # Находим другой активный аккаунт и делаем его основным
                other_account = (
                    db.query(GoogleAccount)
                    .filter(
                        GoogleAccount.user_id == user_id,
                        GoogleAccount.id != account_id,
                        GoogleAccount.is_active == True,
                    )
                    .first()
                )
                if other_account:
                    other_account.is_primary = True

            db.commit()
            return True

        return False

# Создаем экземпляр репозитория
google_account_repository = GoogleAccountRepository()
