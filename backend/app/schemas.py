from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Any, Optional, List, Literal
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
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    google_account_id: int = Field(
        ..., description="ID Google аккаунта для создания опроса"
    )
    google_form_url: HttpUrl
    reward_per_response: int = Field(..., ge=1, le=50)
    responses_needed: Optional[int] = Field(None, ge=1)
    max_responses_per_user: int = Field(1, ge=1, le=10)
    collects_emails: bool = True
    google_account_id: int = Field(..., description="ID Google аккаунта для создания опроса")


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


# Error schemas
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[dict] = None


class FormInfo:
    title: str
    documentTitle: str
    description: Optional[str]


class QuizSettings:
    isQuiz: Optional[bool]


type EmailCollectionType = Optional[
        Literal[
            "EMAIL_COLLECTION_TYPE_UNSPECIFIED",
            "DO_NOT_COLLECT",
            "VERIFIED",
            "RESPONDER_INPUT",
        ]
    ]

class FormSettings:
    quizSettings: Optional[QuizSettings]
    emailCollectionType: EmailCollectionType = "EMAIL_COLLECTION_TYPE_UNSPECIFIED"
    collect_emails: Optional[bool] = True if emailCollectionType in ["VERIFIED", "RESPONDER_INPUT"] else False


class FormItem:
    itemId: str
    title: str
    description: Optional[str] = None

    questionItem: Optional[dict[str, Any]] = None  # Можно расширить для конкретных типов вопросов
    questionGroupItem: Optional[dict[str, Any]] = None  # Можно расширить для групп вопросов
    pageBreakItem: Optional[dict[str, Any]] = None  # Можно расширить для разрывов страниц
    textItem: Optional[dict[str, Any]] = None  # Можно расширить для текстовых элементов
    imageItem: Optional[dict[str, Any]] = None  # Можно расширить для изображений
    videoItem: Optional[dict[str, Any]] = None  # Можно расширить для видео


class PublishState:
    isPublished: Optional[bool]
    isAcceptingResponses: Optional[bool]


class PublishSettings:
    publishState: Optional[PublishState]


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