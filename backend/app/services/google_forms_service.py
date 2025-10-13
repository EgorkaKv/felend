from typing import Dict, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
from app.core.exceptions import GoogleAPIException


logger = logging.getLogger(__name__)

class GoogleFormsService:
    """Сервис для работы с Google Forms API"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.credentials = Credentials(token=access_token)
        self.service = build('forms', 'v1', credentials=self.credentials)
    
    async def get_form_info(self, form_id: str) -> Dict[str, Any]:
        """Получить информацию о форме"""
        try:
            form = self.service.forms().get(formId=form_id).execute()
            
            return {
                "form_id": form.get("formId"),
                "title": form.get("info", {}).get("title", ""),
                "description": form.get("info", {}).get("description", ""),
                "document_title": form.get("info", {}).get("documentTitle", ""),
                "response_url": form.get("responderUri", ""),
                "questions_count": len(form.get("items", [])),
                "settings": form.get("settings", {}),
                "linked_sheet_id": form.get("linkedSheetId")
            }
        except HttpError as e:
            logger.error(f"HTTP ошибка при получении формы {form_id}: {e}")
            if e.resp.status == 404:
                raise GoogleAPIException("Форма не найдена или недоступна")
            elif e.resp.status == 403:
                raise GoogleAPIException("Нет доступа к форме")
            else:
                raise GoogleAPIException("Ошибка при получении информации о форме")
        except Exception as e:
            logger.error(f"Ошибка получения информации о форме {form_id}: {e}")
            raise GoogleAPIException("Не удалось получить информацию о форме")
    
    async def get_form_responses(self, form_id: str, page_token: Optional[str] = None) -> Dict[str, Any]:
        """Получить ответы на форму"""
        try:
            request = self.service.forms().responses().list(formId=form_id)
            if page_token:
                request = request.execute(pageToken=page_token)
            else:
                request = request.execute()
            
            responses = request.get("responses", [])
            next_page_token = request.get("nextPageToken")
            
            return {
                "responses": responses,
                "next_page_token": next_page_token,
                "total_responses": len(responses)
            }
        except HttpError as e:
            logger.error(f"HTTP ошибка при получении ответов формы {form_id}: {e}")
            if e.resp.status == 404:
                raise GoogleAPIException("Форма не найдена или недоступна")
            elif e.resp.status == 403:
                raise GoogleAPIException("Нет доступа к ответам формы")
            else:
                raise GoogleAPIException("Ошибка при получении ответов формы")
        except Exception as e:
            logger.error(f"Ошибка получения ответов формы {form_id}: {e}")
            raise GoogleAPIException("Не удалось получить ответы формы")
    
    async def validate_form_access(self, form_id: str) -> bool:
        """Проверить доступ к форме"""
        try:
            await self.get_form_info(form_id)
            return True
        except GoogleAPIException:
            return False
    
    @staticmethod
    def extract_form_id_from_url(form_url: str) -> Optional[str]:
        """Извлечь ID формы из URL"""
        import re
        
        # Паттерн для извлечения ID из Google Forms URL
        pattern = r'forms\.gle/([a-zA-Z0-9_-]+)|/forms/d/([a-zA-Z0-9_-]+)'
        match = re.search(pattern, form_url)
        
        if match:
            return match.group(1) or match.group(2)
        return None


def get_google_forms_service(access_token: str):
    """Фабрика для создания сервиса Google Forms"""
    from app.core.config import settings
    
    if settings.USE_MOCK_GOOGLE_API:
        from app.services.mock_google_service import get_mock_google_forms_service
        return get_mock_google_forms_service(access_token)
    else:
        return GoogleFormsService(access_token)