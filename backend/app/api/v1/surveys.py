from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import (
    get_db,
    get_current_active_user,
    get_current_user_optional,
    get_google_forms_service_with_account,
)
from app.api.deps import get_survey_service
from app.schemas import (
    SurveyCreate,
    SurveyUpdate,
    SurveyListItem,
    SurveyDetail,
    MySurveyDetail,
    ApiResponse,
)
from app.models import User
from app.services.google_forms_service import GoogleFormsService
from app.services.survey_service import SurveyService
from app.core.exceptions import (
    SurveyNotFoundException,
    AuthorizationException,
    ValidationException,
    InsufficientBalanceException,
)


router = APIRouter(prefix="/surveys", tags=["Surveys"])


@router.get("", response_model=List[SurveyListItem])
async def get_surveys_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, min_length=1),
    survey_service: SurveyService = Depends(get_survey_service),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Получить ленту активных опросов"""
    try:
        current_user_id = current_user.id if current_user else None

        if search:
            # TODO: Реализовать поиск через survey_service
            surveys = survey_service.get_surveys_feed(current_user_id, skip, limit)
        else:
            surveys = survey_service.get_surveys_feed(current_user_id, skip, limit)

        return surveys

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching surveys: {str(e)}",
        )


@router.get("/{survey_id}", response_model=SurveyDetail)
async def get_survey_detail(
    survey_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    survey_service: SurveyService = Depends(get_survey_service),
):
    """Получить детали конкретного опроса"""
    try:
        current_user_id = current_user.id if current_user else None
        survey = survey_service.get_survey_detail(survey_id, current_user_id)
        return survey

    except SurveyNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching survey: {str(e)}",
        )


@router.get("/my/", response_model=List[MySurveyDetail])
async def get_my_surveys(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    survey_service: SurveyService = Depends(get_survey_service),
):
    """Получить список моих опросов"""
    try:
        surveys = survey_service.get_my_surveys(current_user.id, skip, limit)
        return surveys

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user surveys: {str(e)}",
        )


@router.post("/my/", 
             #response_model=MySurveyDetail, 
             status_code=status.HTTP_201_CREATED)
async def create_survey(
    survey_data: SurveyCreate,
    current_user: User = Depends(get_current_active_user),
    survey_service: SurveyService = Depends(get_survey_service),
    forms_service: GoogleFormsService = Depends(get_google_forms_service_with_account),
):
    """Создать новый опрос"""
    try:
        survey = survey_service.create_survey(
            survey_data, current_user.id, forms_service
        )

        return survey

        # Возвращаем детальную информацию о созданном опросе
        # Freturn survey_service.get_my_survey_detail(survey.id, current_user.id)

    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except InsufficientBalanceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating survey: {str(e)}",
        )


@router.get("/my/{survey_id}", response_model=MySurveyDetail)
async def get_my_survey_detail(
    survey_id: int,
    current_user: User = Depends(get_current_active_user),
    survey_service: SurveyService = Depends(get_survey_service),
):
    """Получить детали моего опроса"""
    try:
        survey = survey_service.get_my_survey_detail(survey_id, current_user.id)
        return survey

    except SurveyNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except AuthorizationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching survey: {str(e)}",
        )


@router.put("/my/{survey_id}", response_model=MySurveyDetail)
async def update_survey(
    survey_id: int,
    survey_update: SurveyUpdate,
    current_user: User = Depends(get_current_active_user),
    survey_service: SurveyService = Depends(get_survey_service),
):
    """Обновить мой опрос"""
    try:
        survey = survey_service.update_survey(survey_id, survey_update, current_user.id)

        # Возвращаем обновленную информацию
        return survey_service.get_my_survey_detail(survey.id, current_user.id)

    except SurveyNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except AuthorizationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating survey: {str(e)}",
        )


@router.delete("/my/{survey_id}", response_model=ApiResponse)
async def delete_survey(
    survey_id: int,
    current_user: User = Depends(get_current_active_user),
    survey_service: SurveyService = Depends(get_survey_service),
):
    """Удалить мой опрос"""
    try:
        success = survey_service.delete_survey(survey_id, current_user.id)

        return ApiResponse(success=success, message="Survey deleted successfully")

    except SurveyNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except AuthorizationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting survey: {str(e)}",
        )
