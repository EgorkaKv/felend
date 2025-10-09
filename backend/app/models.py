from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base
import enum
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


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # может быть None для Google auth
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    full_name = Column(String(255), nullable=False)
    balance = Column(Integer, default=0)  # баллы пользователя
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Связи
    surveys = relationship("Survey", back_populates="author")
    survey_responses = relationship("SurveyResponse", back_populates="respondent")
    transactions = relationship("BalanceTransaction", back_populates="user")


class Survey(Base):
    __tablename__ = "surveys"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Google Forms интеграция
    google_form_id = Column(String(255), unique=True, nullable=False)  # ID Google формы
    google_form_url = Column(String(1000), nullable=False)  # Ссылка на форму
    google_responses_url = Column(String(1000), nullable=True)  # Ссылка на ответы
    
    # Метаданные формы
    questions_count = Column(Integer, nullable=False, default=0)  # количество вопросов
    question_types = Column(JSONB, nullable=True)  # типы вопросов в JSON формате
    # Пример: {"questions": [{"type": "text", "required": true}, {"type": "choice", "options": ["Да", "Нет"]}]}
    
    # Система баллов и статус
    reward_per_response = Column(Integer, nullable=False)  # баллы за прохождение
    status = Column(SQLEnum(SurveyStatus), default=SurveyStatus.DRAFT)
    
    # Статистика
    total_responses = Column(Integer, default=0)  # общее количество ответов
    responses_needed = Column(Integer, nullable=True)  # желаемое количество ответов
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Связи
    author = relationship("User", back_populates="surveys")
    responses = relationship("SurveyResponse", back_populates="survey")
    transactions = relationship("BalanceTransaction", foreign_keys="BalanceTransaction.related_survey_id", back_populates="related_survey")





class SurveyResponse(Base):
    __tablename__ = "survey_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    respondent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Google Forms данные
    google_response_id = Column(String(255), unique=True, nullable=True)  # ID ответа в Google Forms
    google_timestamp = Column(DateTime(timezone=True), nullable=True)  # время из Google Forms
    
    # Метаданные
    is_verified = Column(Boolean, default=False)  # проверен ли ответ
    reward_paid = Column(Boolean, default=False)  # выплачена ли награда
    
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    survey = relationship("Survey", back_populates="responses")
    respondent = relationship("User", back_populates="survey_responses")


class BalanceTransaction(Base):
    __tablename__ = "balance_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Integer, nullable=False)  # может быть отрицательным для трат
    balance_after = Column(Integer, nullable=False)  # баланс после транзакции
    description = Column(String(500), nullable=True)  # описание транзакции
    related_survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=True)  # связанный опрос
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    user = relationship("User", back_populates="transactions")
    related_survey = relationship("Survey")