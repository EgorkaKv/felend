"""
Google Forms endpoints (валидация формы и т.п.)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_google_forms_service
from app.core.exceptions import GoogleAPIException
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/forms/validate")
async def validate_google_form(
    form_url: str,
    forms_service = Depends(get_google_forms_service)
):
    """
    Валидировать Google Form URL и проверить доступ
    """
    form_id = forms_service.extract_form_id_from_url(form_url)
    if not form_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный URL Google Forms"
        )
    try:
        form_info = await forms_service.get_form_info(form_id)
        return {
            "valid": True,
            "form_id": form_id,
            "form_info": form_info
        }
    except GoogleAPIException as e:
        return {
            "valid": False,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Error validating form: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при проверке формы"
        )
