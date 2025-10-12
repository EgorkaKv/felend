"""
Сервис для управления пользователями (user_service)
"""

from typing import List
from sqlalchemy.orm import Session
from app.models import User, BalanceTransaction
from app.repositories.user_repository import user_repository
from app.schemas import UserUpdate, UserProfile, TransactionItem

class UserService:
    """Сервис для работы с пользователями"""
    def __init__(self, db: Session):
        self.user_repo = user_repository
        self.db = db

    def update_profile(self, user: User, user_update: UserUpdate) -> User:
        """Обновить профиль пользователя"""
        updated_user = self.user_repo.update(self.db, user, user_update)
        return updated_user

    def get_transactions(self, user: User, skip: int = 0, limit: int = 50) -> List[TransactionItem]:
        """Получить историю транзакций пользователя с информацией о связанных опросах"""
        transactions = (
            self.db.query(BalanceTransaction)
            .filter(BalanceTransaction.user_id == user.id)
            .order_by(BalanceTransaction.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        result = []
        for transaction in transactions:
            transaction_data = TransactionItem.model_validate(transaction)
            if transaction.related_survey_id:
                from app.models import Survey
                survey = self.db.query(Survey).filter(Survey.id == transaction.related_survey_id).first()
                if survey:
                    transaction_data.related_survey = {
                        "id": survey.id,
                        "title": survey.title
                    }
            result.append(transaction_data)
        return result
