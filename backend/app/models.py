from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.database import Base
import enum
from typing import Optional
from datetime import datetime

class TransactionType(enum.Enum):
    EARNED = "earned"  # получил баллы за прохождение опроса
    SPENT = "spent"    # потратил баллы на получение ответов
    BONUS = "bonus"    # приветственный бонус


class SurveyStatus(enum.Enum):
    DRAFT = "draft"           # черновик
    ACTIVE = "active"         # активный
    PAUSED = "paused"         # приостановлен
    COMPLETED = "completed"   # завершен


class VerificationType(str, enum.Enum):
    """Тип верификации - используем str для правильной сериализации"""
    email_verification = "email_verification"  # верификация email при регистрации
    password_reset = "password_reset"          # сброс пароля


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # может быть None для Google auth
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    balance: Mapped[int] = mapped_column(Integer, default=0)  # баллы пользователя
    
    # Постоянный код респондента для каждого пользователя
    respondent_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # RESP_123456789
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Связи
    google_accounts = relationship("GoogleAccount", back_populates="user")
    survey_responses = relationship("SurveyResponse", back_populates="respondent")
    transactions = relationship("BalanceTransaction", back_populates="user")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "balance": self.balance,
            "respondent_code": self.respondent_code,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class GoogleAccount(Base):
    __tablename__ = "google_account"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Google OAuth данные
    google_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)  # Google user ID
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # Google email
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # Google display name
    
    # Google API токены
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Статус аккаунта
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)  # основной Google аккаунт для пользователя
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Связи
    user = relationship("User", back_populates="google_accounts")
    surveys = relationship("Survey", back_populates="google_account")


class Survey(Base):
    __tablename__ = "surveys"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    google_account_id: Mapped[int] = mapped_column(Integer, ForeignKey("google_account.id", ondelete="CASCADE"), nullable=False)
    
    # Google Forms интеграция
    google_form_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)  # ID Google формы
    google_form_url: Mapped[str] = mapped_column(String(1000), nullable=False)  # Ссылка на форму
    google_responses_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)  # Ссылка на ответы
    
    # Метаданные формы
    questions_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # количество вопросов
    question_types: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # типы вопросов в JSON формате
    # Пример: {"questions": [{"type": "text", "required": true}, {"type": "choice", "options": ["Да", "Нет"]}]}
    max_responses_per_user: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # Система баллов и статус
    reward_per_response: Mapped[int] = mapped_column(Integer, nullable=False)  # баллы за прохождение
    status: Mapped[SurveyStatus] = mapped_column(SQLEnum(SurveyStatus), default=SurveyStatus.DRAFT)
    
    # Статистика
    total_responses: Mapped[int] = mapped_column(Integer, default=0)  # общее количество ответов
    responses_needed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # желаемое количество ответов
    last_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # когда в последний раз проверяли форму
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Связи
    google_account = relationship("GoogleAccount", back_populates="surveys")
    responses = relationship("SurveyResponse", back_populates="survey")
    transactions = relationship("BalanceTransaction", foreign_keys="BalanceTransaction.related_survey_id", back_populates="related_survey")


class SurveyResponse(Base):
    __tablename__ = "survey_responses"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    survey_id: Mapped[int] = mapped_column(Integer, ForeignKey("surveys.id"), nullable=False)
    respondent_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Google Forms данные
    google_response_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)  # ID ответа в Google Forms
    google_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # время из Google Forms
    
    # Метаданные
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)  # проверен ли ответ
    reward_paid: Mapped[bool] = mapped_column(Boolean, default=False)  # выплачена ли награда
    
    # Временные метки
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())  # когда начал участие
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # когда завершил и получил баллы
    
    # Связи
    survey = relationship("Survey", back_populates="responses")
    respondent = relationship("User", back_populates="survey_responses")


class BalanceTransaction(Base):
    __tablename__ = "balance_transactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # может быть отрицательным для трат
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)  # баланс после транзакции
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # описание транзакции
    related_survey_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("surveys.id"), nullable=True)  # связанный опрос
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    user = relationship("User", back_populates="transactions")
    related_survey = relationship("Survey")


class EmailVerification(Base):
    """Модель для хранения токенов и кодов верификации email + временное хранение данных пользователя"""
    __tablename__ = "email_verifications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable для новых регистраций
    verification_type: Mapped[VerificationType] = mapped_column(
        SQLEnum(VerificationType), 
        nullable=False, 
        default=VerificationType.email_verification
    )
    verification_token: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)  # UUID4
    verification_code: Mapped[Optional[str]] = mapped_column(String(6), nullable=True)  # 6-значный код
    code_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # код действителен 15 минут
    token_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)  # токен действителен 24 часа
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)  # был ли использован для успешной верификации
    attempts: Mapped[int] = mapped_column(Integer, default=0)  # количество неудачных попыток ввода кода
    last_code_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # для rate limiting
    
    # Временные данные пользователя (для email_verification типа)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)  # Email пользователя
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Хэшированный пароль
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Полное имя
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Связь с пользователем (опциональная)
    user = relationship("User")