from fastapi import APIRouter, Body, Depends, status, Query
from typing import List, Optional

from pydantic import HttpUrl
from app.api.deps import (
    get_current_active_user,
    get_current_user_optional,
    get_google_accounts_service,
)
from app.api.deps import get_survey_service
from app.schemas import (
    GoogleForm,
    SurveyCreate,
    SurveyUpdate,
    SurveyListItem,
    SurveyDetail,
    MySurveyDetail,
    ApiResponse,
    ErrorResponse,
    SurveyValidationResponse,
)
from app.models import User
from app.services.google_forms_service import GoogleFormsService
from app.services.survey_service import SurveyService
from app.services.google_accounts_service import GoogleAccountsService


router = APIRouter(prefix="/surveys", tags=["Surveys"])


@router.get(
    "", 
    response_model=List[SurveyListItem],
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def get_surveys_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, min_length=1),
    survey_service: SurveyService = Depends(get_survey_service),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Получить ленту активных опросов"""
    current_user_id = current_user.id if current_user else None

    if search:
        # TODO: Реализовать поиск через survey_service
        surveys = survey_service.get_surveys_feed(current_user_id, skip, limit)
    else:
        surveys = survey_service.get_surveys_feed(current_user_id, skip, limit)

    return surveys


@router.get(
    "/{survey_id}", 
    response_model=SurveyDetail,
    responses={
        404: {"model": ErrorResponse, "description": "Survey not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def get_survey_detail(
    survey_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    survey_service: SurveyService = Depends(get_survey_service),
):
    """Получить детали конкретного опроса"""
    current_user_id = current_user.id if current_user else None
    survey = survey_service.get_survey_detail(survey_id, current_user_id)
    return survey


@router.get(
    "/my/", 
    response_model=List[MySurveyDetail],
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def get_my_surveys(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    google_account_id: Optional[int] = Query(None, description="ID Google аккаунта (если не указан, используется primary)"),
    current_user: User = Depends(get_current_active_user),
    survey_service: SurveyService = Depends(get_survey_service),
):
    """Получить список моих опросов"""
    surveys = survey_service.get_my_surveys(
        user_id=current_user.id, 
        google_account_id=google_account_id,
        skip=skip, 
        limit=limit
    )
    return surveys


@router.post(
    "/my/", 
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Insufficient balance"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def create_survey(
    survey_data: SurveyCreate,
    current_user: User = Depends(get_current_active_user),
    survey_service: SurveyService = Depends(get_survey_service),
    google_accounts_service: GoogleAccountsService = Depends(get_google_accounts_service),
):
    """Создать новый опрос"""
    # Получаем Google аккаунт из тела запроса и проверяем принадлежность пользователю
    google_account = google_accounts_service.check_user_google_account(
        current_user.id, 
        survey_data.google_account_id
    )

    if not google_account:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google not found or inaccessible",
        )
    
    # Создаем GoogleFormsService для этого аккаунта
    from app.api.deps import get_google_forms_service_for_account
    forms_service = get_google_forms_service_for_account(google_account)

    survey = await survey_service.create_survey(
        survey_data, current_user, forms_service
    )
    return survey


@router.post(
    "/validate",
    response_model=SurveyValidationResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid form URL"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "No access to form with this Google account"},
        404: {"model": ErrorResponse, "description": "Google account not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def validate_google_form(
    form_url: HttpUrl = Body(...),
    google_account_id: int = Body(...),
    current_user: User = Depends(get_current_active_user),
    google_accounts_service: GoogleAccountsService = Depends(get_google_accounts_service),
):
    """
    Validate Google Form URL and check access
    """

    # Получаем Google аккаунт из тела запроса и проверяем принадлежность пользователю
    google_account = google_accounts_service.check_user_google_account(
        current_user.id, 
        google_account_id
    )

    # Создаем GoogleFormsService для этого аккаунта
    from app.api.deps import get_google_forms_service_for_account
    forms_service: GoogleFormsService = get_google_forms_service_for_account(google_account)

    validated_form: GoogleForm = await forms_service.validate_form_access(str(form_url))

    return SurveyValidationResponse(
        form_id=validated_form.formId,
        title=validated_form.info.title,
        description=validated_form.info.description,
        collect_emails=validated_form.settings.collect_emails or False,
        questions_count=len(validated_form.items),
        estimated_time_minutes=len(validated_form.items) // 3 + 1,
        min_rewards=10
    )

@router.get(
    "/my/{survey_id}", 
    response_model=MySurveyDetail,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Survey not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def get_my_survey_detail(
    survey_id: int,
    current_user: User = Depends(get_current_active_user),
    survey_service: SurveyService = Depends(get_survey_service),
):
    """Получить детали моего опроса"""
    survey = survey_service.get_my_survey_detail(
        survey_id=survey_id, 
        user_id=current_user.id,
    )
    return survey


@router.put(
    "/my/{survey_id}", 
    response_model=MySurveyDetail,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Survey not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def update_survey(
    survey_id: int,
    survey_update: SurveyUpdate,
    current_user: User = Depends(get_current_active_user),
    survey_service: SurveyService = Depends(get_survey_service),
):
    """Обновить мой опрос"""
    survey = survey_service.update_survey(
        survey_id=survey_id, 
        survey_update=survey_update, 
        user_id=current_user.id,
    )

    # Возвращаем обновленную информацию
    return survey_service.get_my_survey_detail(
        survey_id=survey.id, 
        user_id=current_user.id,
    )


@router.delete(
    "/my/{survey_id}", 
    response_model=ApiResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Survey not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def delete_survey(
    survey_id: int,
    current_user: User = Depends(get_current_active_user),
    survey_service: SurveyService = Depends(get_survey_service),
):
    """Удалить мой опрос"""
    success = survey_service.delete_survey(
        survey_id=survey_id, 
        user_id=current_user.id,
    )
    return ApiResponse(success=success, message="Survey deleted successfully")