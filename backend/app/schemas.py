from pydantic import BaseModel, EmailStr, HttpUrl, Field, model_validator
from typing import Optional, List, Literal, Any, Dict
from datetime import datetime
from app.models import SurveyStatus, TransactionType


# Auth schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    refresh_token: str


# User schemas
class UserProfile(BaseModel):
    id: int
    email: str
    full_name: str
    balance: int
    respondent_code: str
    created_at: datetime

    class ConfigDict:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)


# Google Account schemas
class GoogleAccountDetail(BaseModel):
    id: int
    email: str
    name: str
    is_primary: bool
    is_active: bool
    created_at: datetime

    class ConfigDict:
        from_attributes = True


class GoogleAccountCreate(BaseModel):
    google_id: str
    email: str
    name: str
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    is_primary: bool = False


class GoogleAccountUpdate(BaseModel):
    name: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None


# Survey schemas
class SurveyCreate(BaseModel):
    # title: str = Field(..., min_length=1, max_length=255)
    # description: Optional[str] = None
    google_account_id: int = Field(
        ..., description="ID Google аккаунта для создания опроса"
    )
    google_form_url: HttpUrl
    reward_per_response: int = Field(..., ge=1, le=50)
    responses_needed: Optional[int] = Field(None, ge=1)
    max_responses_per_user: int = Field(1, ge=1, le=10)
    # collects_emails: bool = True


class SurveyUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    reward_per_response: Optional[int] = Field(None, ge=1, le=50)
    responses_needed: Optional[int] = Field(None, ge=1)
    max_responses_per_user: Optional[int] = Field(None, ge=1, le=10)
    status: Optional[SurveyStatus] = None


class SurveyListItem(BaseModel):
    id: int
    title: str
    description: Optional[str]
    author_name: str
    reward_per_response: int
    total_responses: int
    responses_needed: Optional[int]
    questions_count: int
    can_participate: bool
    my_responses_count: int

    class ConfigDict:
        from_attributes = True


class SurveyDetail(BaseModel):
    id: int
    title: str
    description: Optional[str]
    author_name: str
    reward_per_response: int
    total_responses: int
    responses_needed: Optional[int]
    questions_count: int
    google_form_url: str
    collects_emails: bool
    max_responses_per_user: int
    can_participate: bool
    my_responses_count: int
    created_at: datetime

    class ConfigDict:
        from_attributes = True


class MySurveyDetail(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: SurveyStatus
    google_form_url: str
    reward_per_response: int
    responses_needed: Optional[int]
    max_responses_per_user: int
    total_responses: int
    total_spent: int
    questions_count: int
    collects_emails: bool
    created_at: datetime

    class ConfigDict:
        from_attributes = True


# Survey participation schemas
class SurveyStartResponse(BaseModel):
    google_form_url: str
    respondent_code: Optional[str] = None
    instructions: str


class SurveyVerifyResponse(BaseModel):
    verified: bool
    reward_earned: int = 0
    new_balance: int
    message: str


# Survey Response schemas
class SurveyResponseCreate(BaseModel):
    survey_id: int
    respondent_id: Optional[int] = None
    google_response_id: Optional[str] = None


class SurveyResponseUpdate(BaseModel):
    is_verified: Optional[bool] = None
    reward_paid: Optional[bool] = None


class SurveyResponseDetail(BaseModel):
    id: int
    survey_id: int
    respondent_id: int
    is_verified: bool
    reward_paid: bool
    started_at: datetime
    completed_at: Optional[datetime]

    class ConfigDict:
        from_attributes = True


# Transaction schemas
class TransactionItem(BaseModel):
    id: int
    transaction_type: TransactionType
    amount: int
    balance_after: int
    description: str
    created_at: datetime
    related_survey: Optional[dict] = None

    class ConfigDict:
        from_attributes = True


# Response wrappers
class ApiResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[dict] = None


class ListResponse(BaseModel):
    items: List[dict]
    total: int
    page: int = 1
    per_page: int = 50


# Error schemas для единого формата ошибок API
class ErrorDetail(BaseModel):
    """Детали ошибки с контекстной информацией"""
    message: str = Field(..., description="Человекочитаемое сообщение об ошибке")
    code: str = Field(..., description="Уникальный код ошибки (например, AUTH001)")
    type: str = Field(..., description="Тип исключения (например, AuthenticationException)")
    details: Optional[Dict[str, Any]] = Field(None, description="Дополнительная контекстная информация")
    timestamp: str = Field(..., description="Время возникновения ошибки в ISO формате")
    path: Optional[str] = Field(None, description="API endpoint где произошла ошибка")


class ErrorResponse(BaseModel):
    """Стандартный формат ответа с ошибкой"""
    error: ErrorDetail = Field(..., description="Информация об ошибке")
    
    class ConfigDict:
        json_schema_extra = {
            "example": {
                "error": {
                    "message": "Survey not found",
                    "code": "SURVEY001",
                    "type": "SurveyNotFoundException",
                    "details": {"survey_id": 123},
                    "timestamp": "2025-10-19T12:00:00Z",
                    "path": "/api/v1/surveys/123"
                }
            }
        }


class ValidationErrorDetail(BaseModel):
    """Детали ошибок валидации (422)"""
    message: str = "Validation error"
    code: str = "VALIDATION001"
    type: str = "ValidationError"
    details: List[Dict[str, Any]] = Field(..., description="Список ошибок валидации от Pydantic")
    timestamp: str
    path: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """Ответ с ошибками валидации"""
    error: ValidationErrorDetail
    
    class ConfigDict:
        json_schema_extra = {
            "example": {
                "error": {
                    "message": "Validation error",
                    "code": "VALIDATION001", 
                    "type": "ValidationError",
                    "details": [
                        {
                            "type": "string_too_short",
                            "loc": ["body", "title"],
                            "msg": "String should have at least 1 character",
                            "input": ""
                        }
                    ],
                    "timestamp": "2025-10-19T12:00:00Z",
                    "path": "/api/v1/surveys/"
                }
            }
        }


class FormInfo(BaseModel):
    title: str
    documentTitle: str
    description: Optional[str] = None


class QuizSettings(BaseModel):
    isQuiz: Optional[bool] = None


EmailCollectionType = Optional[
    Literal[
        "EMAIL_COLLECTION_TYPE_UNSPECIFIED",
        "DO_NOT_COLLECT",
        "VERIFIED",
        "RESPONDER_INPUT",
    ]
]

class FormSettings(BaseModel):
    quizSettings: Optional[QuizSettings] = None
    emailCollectionType: EmailCollectionType = "EMAIL_COLLECTION_TYPE_UNSPECIFIED"
    collect_emails: Optional[bool] = None

    @model_validator(mode="after")
    def set_collect_emails(self):
        # Если collect_emails не передан явно, вычисляем его по emailCollectionType
        if self.collect_emails is None:
            self.collect_emails = True if self.emailCollectionType in ["VERIFIED", "RESPONDER_INPUT"] else False
        return self


class FormItem(BaseModel):
    itemId: str
    title: str
    description: Optional[str] = None

    questionItem: Optional[dict[str, Any]] = None  # Можно расширить для конкретных типов вопросов
    questionGroupItem: Optional[dict[str, Any]] = None  # Можно расширить для групп вопросов
    pageBreakItem: Optional[dict[str, Any]] = None  # Можно расширить для разрывов страниц
    textItem: Optional[dict[str, Any]] = None  # Можно расширить для текстовых элементов
    imageItem: Optional[dict[str, Any]] = None  # Можно расширить для изображений
    videoItem: Optional[dict[str, Any]] = None  # Можно расширить для видео


class PublishState(BaseModel):
    isPublished: Optional[bool] = None
    isAcceptingResponses: Optional[bool] = None


class PublishSettings(BaseModel):
    publishState: Optional[PublishState] = None


class GoogleForm(BaseModel):
    formId: str
    info: FormInfo
    settings: FormSettings
    items: List[FormItem] = []
    revisionId: Optional[str] = None
    responderUri: Optional[HttpUrl] = None
    publishSettings: Optional[PublishSettings] = None


class FormValidationResponse(BaseModel):
    have_access: bool
    google_form_id: str
    google_form_url: str
    title: Optional[str] = None
    question_count: Optional[int] = 0
    recommended_reward: Optional[int] = 0
    collects_emails: Optional[bool] = None


# Email Verification schemas
class RegisterResponse(BaseModel):
    """Ответ после регистрации с токеном верификации"""
    verification_token: str
    email: str
    message: str = "Registration successful. Please verify your email to activate your account."


class RequestVerificationCode(BaseModel):
    """Запрос на отправку кода верификации"""
    verification_token: str = Field(..., min_length=36, max_length=36)


class VerificationCodeResponse(BaseModel):
    """Ответ после отправки кода верификации"""
    success: bool
    message: str
    email_masked: str  # Маскированный email для безопасности


class VerifyEmail(BaseModel):
    """Запрос на подтверждение email с кодом"""
    verification_token: str = Field(..., min_length=36, max_length=36)
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class EmailVerifiedResponse(BaseModel):
    """Ответ после успешной верификации email"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfile
    message: str = "Email verified successfully. Welcome to Felend!"
