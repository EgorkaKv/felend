"""
Сервис для управления балансом пользователей
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import User, BalanceTransaction, TransactionType
from app.repositories.user_repository import user_repository
from app.core.exceptions import UserNotFoundException


class BalanceService:
    """Сервис для управления балансом пользователей"""
    def __init__(self, db: Session):
        self.user_repo = user_repository
        self.db = db

    def add_bonus_points(self, user_id: int, amount: int, description: str = "Welcome bonus") -> BalanceTransaction:
        user = self.user_repo.get(self.db, user_id)
        if not user:
            raise UserNotFoundException()
        
        # Обновить баланс
        user.balance += amount
        
        # Создать транзакцию
        transaction = BalanceTransaction(
            user_id=user_id,
            transaction_type=TransactionType.BONUS,
            amount=amount,
            balance_after=user.balance,
            description=description
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def get_user_transactions(self, user_id: int, limit: int = 50, offset: int = 0, transaction_type: Optional[TransactionType] = None) -> List[BalanceTransaction]:
        query = self.db.query(BalanceTransaction).filter(BalanceTransaction.user_id == user_id)
        if transaction_type:
            query = query.filter(BalanceTransaction.transaction_type == transaction_type)
        return query.order_by(BalanceTransaction.created_at.desc()).offset(offset).limit(limit).all()

    def get_balance_summary(self, user_id: int) -> dict:
        user = self.user_repo.get(self.db, user_id)
        if not user:
            raise UserNotFoundException()
        earned = self.db.query(BalanceTransaction).filter(
            BalanceTransaction.user_id == user_id,
            BalanceTransaction.transaction_type == TransactionType.EARNED
        ).count()
        spent = self.db.query(BalanceTransaction).filter(
            BalanceTransaction.user_id == user_id,
            BalanceTransaction.transaction_type == TransactionType.SPENT
        ).count()
        return {
            "current_balance": user.balance,
            "total_earned_transactions": earned,
            "total_spent_transactions": spent,
            "user_id": user_id
        }