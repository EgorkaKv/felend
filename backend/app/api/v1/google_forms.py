"""
Google Forms endpoints (валидация формы и т.п.)
"""
from fastapi import APIRouter, Depends, HTTPException, status
#from app.api.deps import get_google_forms_service_with_account
from app.core.exceptions import GoogleAPIException
from app.services.google_forms_service import GoogleFormsService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/forms/validate")
async def validate_google_form(
    form_url: str,
    google_account_id: int,
    #forms_service: GoogleFormsService = Depends(get_google_forms_service_with_account)
    forms_service = lambda: None
):
    """
    Валидировать Google Form URL и проверить доступ
    """
    try:
        validated_form = await forms_service.validate_form_access(form_url)
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
