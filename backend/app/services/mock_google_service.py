"""
Мок-сервис для эмуляции Google Forms API в процессе разработки
"""

from typing import Dict, Any, Optional, List
import random
import string
from datetime import datetime, timezone
import logging

from app.core.exceptions import GoogleAPIException


logger = logging.getLogger(__name__)


class MockGoogleFormsService:
    """Мок-сервис для эмуляции Google Forms API"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        # Симулируем базу данных форм
        self._forms_db = {
            "1FAIpQLSdXYZ123": {
                "formId": "1FAIpQLSdXYZ123",
                "info": {
                    "title": "Опрос о любимых цветах",
                    "description": "Расскажите нам о ваших предпочтениях в цветах",
                    "documentTitle": "Опрос о цветах"
                },
                "responderUri": "https://docs.google.com/forms/d/e/1FAIpQLSdXYZ123/viewform",
                "items": [
                    {"questionId": "q1", "title": "Какой ваш любимый цвет?", "type": "CHOICE"},
                    {"questionId": "q2", "title": "Почему этот цвет вам нравится?", "type": "TEXT"},
                    {"questionId": "q3", "title": "Ваш email", "type": "TEXT"}
                ],
                "settings": {
                    "requireLogin": False
                },
                "linkedSheetId": None
            },
            "1FAIpQLSdABC456": {
                "formId": "1FAIpQLSdABC456", 
                "info": {
                    "title": "Исследование пользовательского опыта",
                    "description": "Помогите нам улучшить наш продукт",
                    "documentTitle": "UX Research"
                },
                "responderUri": "https://docs.google.com/forms/d/e/1FAIpQLSdABC456/viewform",
                "items": [
                    {"questionId": "q1", "title": "Как часто вы используете наш продукт?", "type": "CHOICE"},
                    {"questionId": "q2", "title": "Что вам больше всего нравится?", "type": "TEXT"},
                    {"questionId": "q3", "title": "Что нужно улучшить?", "type": "TEXT"},
                    {"questionId": "q4", "title": "Ваш контактный email", "type": "TEXT"}
                ],
                "settings": {
                    "requireLogin": False
                },
                "linkedSheetId": None
            }
        }
        
        # Симулируем ответы на формы
        self._responses_db = {
            "1FAIpQLSdXYZ123": [
                {
                    "responseId": "resp_001",
                    "createTime": "2025-10-11T08:30:00Z",
                    "lastSubmittedTime": "2025-10-11T08:32:00Z",
                    "respondentEmail": "user1@example.com",
                    "answers": {
                        "q1": {"textAnswers": {"answers": [{"value": "Синий"}]}},
                        "q2": {"textAnswers": {"answers": [{"value": "Он успокаивает меня"}]}},
                        "q3": {"textAnswers": {"answers": [{"value": "user1@example.com"}]}}
                    }
                },
                {
                    "responseId": "resp_002", 
                    "createTime": "2025-10-11T09:15:00Z",
                    "lastSubmittedTime": "2025-10-11T09:18:00Z",
                    "respondentEmail": "user2@example.com",
                    "answers": {
                        "q1": {"textAnswers": {"answers": [{"value": "Зеленый"}]}},
                        "q2": {"textAnswers": {"answers": [{"value": "Напоминает о природе"}]}},
                        "q3": {"textAnswers": {"answers": [{"value": "user2@example.com"}]}}
                    }
                }
            ],
            "1FAIpQLSdABC456": [
                {
                    "responseId": "resp_003",
                    "createTime": "2025-10-11T10:00:00Z", 
                    "lastSubmittedTime": "2025-10-11T10:05:00Z",
                    "respondentEmail": "user3@example.com",
                    "answers": {
                        "q1": {"textAnswers": {"answers": [{"value": "Ежедневно"}]}},
                        "q2": {"textAnswers": {"answers": [{"value": "Простота интерфейса"}]}},
                        "q3": {"textAnswers": {"answers": [{"value": "Больше настроек"}]}},
                        "q4": {"textAnswers": {"answers": [{"value": "user3@example.com"}]}}
                    }
                }
            ]
        }
    
    async def get_form_info(self, form_id: str) -> Dict[str, Any]:
        """Получить информацию о форме (мок)"""
        
        # Симулируем задержку API
        await self._simulate_api_delay()
        
        if form_id not in self._forms_db:
            raise GoogleAPIException("Форма не найдена или недоступна")
        
        form_data = self._forms_db[form_id]
        
        logger.info(f"Mock: Retrieved form info for {form_id}")
        
        return {
            "form_id": form_data["formId"],
            "title": form_data["info"]["title"],
            "description": form_data["info"]["description"], 
            "document_title": form_data["info"]["documentTitle"],
            "response_url": form_data["responderUri"],
            "questions_count": len(form_data["items"]),
            "settings": form_data["settings"],
            "linked_sheet_id": form_data.get("linkedSheetId")
        }
    
    async def get_form_responses(self, form_id: str, page_token: Optional[str] = None) -> Dict[str, Any]:
        """Получить ответы на форму (мок)"""
        
        # Симулируем задержку API
        await self._simulate_api_delay()
        
        if form_id not in self._responses_db:
            logger.info(f"Mock: No responses found for form {form_id}")
            return {
                "responses": [],
                "next_page_token": None,
                "total_responses": 0
            }
        
        responses = self._responses_db[form_id]
        
        # Симулируем пагинацию
        page_size = 10
        start_idx = 0
        if page_token:
            try:
                start_idx = int(page_token)
            except (ValueError, TypeError):
                start_idx = 0
        
        end_idx = start_idx + page_size
        page_responses = responses[start_idx:end_idx]
        
        next_page_token = None
        if end_idx < len(responses):
            next_page_token = str(end_idx)
        
        logger.info(f"Mock: Retrieved {len(page_responses)} responses for form {form_id}")
        
        return {
            "responses": page_responses,
            "next_page_token": next_page_token,
            "total_responses": len(page_responses)
        }
    
    async def validate_form_access(self, form_id: str) -> bool:
        """Проверить доступ к форме (мок)"""
        await self._simulate_api_delay()
        return form_id in self._forms_db
    
    @staticmethod
    def extract_form_id_from_url(form_url: str) -> Optional[str]:
        """Извлечь ID формы из URL (настоящая логика)"""
        import re
        
        # Паттерн для извлечения ID из Google Forms URL
        pattern = r'forms\.gle/([a-zA-Z0-9_-]+)|/forms/d/([a-zA-Z0-9_-]+)'
        match = re.search(pattern, form_url)
        
        if match:
            return match.group(1) or match.group(2)
        return None
    
    async def _simulate_api_delay(self):
        """Симулировать задержку реального API"""
        import asyncio
        # Случайная задержка от 100мс до 500мс
        delay = random.uniform(0.1, 0.5)
        await asyncio.sleep(delay)
    
    def add_mock_response(self, form_id: str, respondent_email: str, respondent_code: str = ''):
        """Добавить мок-ответ (для тестирования)"""
        if form_id not in self._responses_db:
            self._responses_db[form_id] = []
        
        response_id = f"resp_{self._generate_random_id()}"
        now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        # Получаем структуру формы
        form = self._forms_db.get(form_id)
        if not form:
            return None
        
        # Генерируем случайные ответы
        answers = {}
        for item in form["items"]:
            q_id = item["questionId"]
            if item["title"].lower().find("email") != -1:
                # Если вопрос про email, используем предоставленный email
                answers[q_id] = {"textAnswers": {"answers": [{"value": respondent_email}]}}
            elif item["title"].lower().find("код") != -1 and respondent_code:
                # Если вопрос про код респондента
                answers[q_id] = {"textAnswers": {"answers": [{"value": respondent_code}]}}
            elif item["type"] == "CHOICE":
                # Для выбора генерируем случайный ответ
                choices = ["Отлично", "Хорошо", "Нормально", "Плохо"]
                answers[q_id] = {"textAnswers": {"answers": [{"value": random.choice(choices)}]}}
            else:
                # Для текстовых вопросов генерируем случайный текст
                texts = ["Очень интересно", "Мне нравится", "Хорошо сделано", "Можно улучшить"]
                answers[q_id] = {"textAnswers": {"answers": [{"value": random.choice(texts)}]}}
        
        mock_response = {
            "responseId": response_id,
            "createTime": now,
            "lastSubmittedTime": now,
            "respondentEmail": respondent_email,
            "answers": answers
        }
        
        self._responses_db[form_id].append(mock_response)
        logger.info(f"Mock: Added response {response_id} for form {form_id}")
        
        return mock_response
    
    def _generate_random_id(self) -> str:
        """Генерировать случайный ID"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


def get_mock_google_forms_service(access_token: str) -> MockGoogleFormsService:
    """Фабрика для создания мок-сервиса Google Forms"""
    return MockGoogleFormsService(access_token)