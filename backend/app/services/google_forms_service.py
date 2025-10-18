from typing import Dict, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
import logging
from app.core.exceptions import GoogleAPIException, ValidationException
from app.schemas import EmailCollectionType, FormValidationResponse, GoogleForm


logger = logging.getLogger(__name__)


class GoogleFormsService:
    """Сервис для работы с Google Forms API"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.credentials = Credentials(token=access_token)
        self.service = build("forms", "v1", credentials=self.credentials)

    async def get_form_info(self, form_id: str) -> GoogleForm:
        """Получить информацию о форме"""
        try:
            form_data = self.service.forms().get(formId=form_id).execute()
            
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
        
        # Проверяем что получили данные
        if not form_data:
            raise GoogleAPIException("Форма не найдена - пустой ответ от API")
        
        # Проверяем наличие обязательных полей
        if 'formId' not in form_data:
            raise GoogleAPIException("Некорректный ответ от Google API - отсутствует formId")
        
        # Валидируем данные через Pydantic
        try:
            return GoogleForm(**form_data)
        except Exception as validation_error:
            logger.error(f"Ошибка валидации данных формы {form_id}: {validation_error}")
            logger.error(f"Полученные данные: {form_data}")
            raise GoogleAPIException(f"Некорректная структура данных от Google API: {str(validation_error)}")

    async def get_form_responses(
        self, form_id: str, page_token: Optional[str] = None
    ) -> Dict[str, Any]:
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
                "total_responses": len(responses),
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

    async def validate_form_access(self, url: str) -> GoogleForm:
        """Валидировать доступ к Google Forms через API"""

        # Извлечь ID формы из URL
        form_id = GoogleFormsService.extract_form_id_from_url(url)
        if not form_id:
            raise ValidationException("Invalid Google Forms URL format")

        try:
            return await self.get_form_info(form_id)
        
        except Exception as e:
            raise ValidationException(f"Cannot access Google Form: {str(e)}")
        

    @staticmethod
    def extract_form_id_from_url(form_url: str) -> Optional[str]:
        """Извлечь ID формы из URL"""
        import re
 
        # Регулярное выражение для Google Forms URL
        google_forms_pattern = r"https://docs\.google\.com/forms/d/([a-zA-Z0-9-_]+)"
        short_url_pattern = r"https://forms\.gle/([a-zA-Z0-9-_]+)"

        form_id = None

        # Проверяем длинный URL
        match = re.match(google_forms_pattern, form_url)
        if match:
            form_id = match.group(1)
        else:
            # Проверяем короткий URL
            match = re.match(short_url_pattern, form_url)
            if match:
                form_id = match.group(1)

        if not form_id:
            raise ValidationException("Invalid Google Forms URL format")
        
        return form_id

    def check_identifaction_questions(self, form: GoogleForm) -> None:
        """Проверить наличие идентификационных вопросов в форме"""
        pass
        '''TITLE = 'User ID (Optional)'
        try:
            items = form.items

            # Item с нужным тайтлом + типом textQuestion
            # или группа вопросов с такими вопросами внутри
            
            for item in items:
                item_id = item.get("itemId")
                item_title = item.get("title", "").lower()
                question = item.questionItem.get("textQuestion") if item.get("questionItem") else None
                if item_title.lower() == TITLE.lower() and question:
                    return True
            return False
        
        except Exception as e:
            logger.error(f"Ошибка проверки идентификационных вопросов для формы {form_id}: {e}")
            raise GoogleAPIException("Не удалось проверить идентификационные вопросы формы")'''

    async def change_collection_emails_type(self, form_id: str, new_type: EmailCollectionType):
        """Изменить тип сбора email в настройках формы"""
        try:
            # Получаем текущие настройки формы
            form = await self.get_form_info(form_id)
            current_settings = form.settings

            # Обновляем тип сбора email
            current_settings.emailCollectionType = new_type

            # Отправляем обновленные настройки обратно в Google Forms API
            update_body = {
                "settings": {
                    "emailCollectionType": new_type
                }
            }

            updated_form = self.service.forms().update(
                formId=form_id,
                body=update_body
            ).execute()

            return GoogleForm(**updated_form)

        except HttpError as e:
            logger.error(f"HTTP ошибка при изменении типа сбора email для формы {form_id}: {e}")
            raise GoogleAPIException("Ошибка при изменении настроек формы")
        except Exception as e:
            logger.error(f"Ошибка при изменении типа сбора email для формы {form_id}: {e}")
            raise GoogleAPIException("Не удалось изменить настройки формы")


def get_google_forms_service(access_token: str):
    """Фабрика для создания сервиса Google Forms"""
    from app.core.config import settings

    if settings.USE_MOCK_GOOGLE_API:
        from app.services.mock_google_service import get_mock_google_forms_service

        return get_mock_google_forms_service(access_token)
    else:
        return GoogleFormsService(access_token)
