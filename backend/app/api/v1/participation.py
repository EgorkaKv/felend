"""
API endpoints для участия в опросах
"""

from fastapi import APIRouter, Depends

from typing import Dict, Any

from app.api.deps import get_current_active_user, get_participation_service
from app.models import User
from app.services.participation_service import ParticipationService
from app.schemas import SurveyStartResponse, SurveyVerifyResponse, ErrorResponse


router = APIRouter(tags=["Participation"], prefix="/surveys")


@router.post(
    "/{survey_id}/participate", 
    response_model=SurveyStartResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Survey not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def start_survey_participation(
    survey_id: int,
    current_user: User = Depends(get_current_active_user),
    participation_service: ParticipationService = Depends(get_participation_service)
):
    """
    Начать участие в опросе
    
    Возвращает ссылку на Google Form и инструкции для участия
    """
    result = participation_service.start_participation(survey_id, current_user.id)
    return result


@router.post(
    "/{survey_id}/verify", 
    response_model=SurveyVerifyResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Survey not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def verify_survey_completion(
    survey_id: int,
    current_user: User = Depends(get_current_active_user),
    participation_service: ParticipationService = Depends(get_participation_service)
):
    """
    Засчитать завершение опроса и начислить баллы
    
    Вызывается после того, как пользователь заполнил Google Form
    """
    result = participation_service.verify_and_reward(survey_id, current_user.id)
    return result


@router.get("/{survey_id}/my-status")
async def get_my_participation_status(
    survey_id: int,
    current_user: User = Depends(get_current_active_user),
    participation_service: ParticipationService = Depends(get_participation_service)
) -> Dict[str, Any]:
    """
    Получить статус моего участия в опросе
    """
    status_info = participation_service.get_user_participation_status(survey_id, current_user.id)
    return {
        "success": True,
        "data": status_info
    }


@router.get("/my-responses")
async def get_my_responses(
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_active_user),
    participation_service: ParticipationService = Depends(get_participation_service)
):
    """
    Получить мои ответы на опросы
    """
    offset = (page - 1) * per_page
    responses = participation_service.response_repo.get_user_responses(
        participation_service.db, current_user.id, per_page, offset
    )
    
    # Подготовить данные для ответа
    response_data = []
    for response in responses:
        survey = response.survey
        response_data.append({
            "id": response.id,
            "survey": {
                "id": survey.id,
                "title": survey.title,
                "reward_per_response": survey.reward_per_response
            },
            "started_at": response.started_at,
            "completed_at": response.completed_at,
            "reward_earned": survey.reward_per_response if response.reward_paid else 0,
            "status": "completed" if response.is_verified else "in_progress"
        })
    
    return {
        "success": True,
        "data": {
            "items": response_data,
            "page": page,
            "per_page": per_page,
            "total": len(response_data)
        }
    }