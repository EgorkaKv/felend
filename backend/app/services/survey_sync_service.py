"""
Сервис для синхронизации ответов из Google Forms
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging

from app.models import Survey, SurveyResponse, User
from app.repositories.survey_repository import survey_repository
from app.repositories.survey_response_repository import survey_response_repository
from app.repositories.user_repository import user_repository

from app.core.exceptions import GoogleAPIException, ValidationException



logger = logging.getLogger(__name__)


class SurveySyncService:
    """Сервис для синхронизации ответов из Google Forms"""
    
    def __init__(self):
        self.survey_repo = survey_repository
        self.response_repo = survey_response_repository
        self.user_repo = user_repository
    
    async def sync_survey_responses(
        self, 
        db: Session, 
        survey_id: int, 
        force_full_sync: bool = False
    ) -> Any:
        """Синхронизировать ответы для конкретного опроса"""
        
        # Получить опрос
        survey = self.survey_repo.get(db, survey_id)
        if not survey:
            raise ValidationException("Survey not found")
        
        # Получить автора опроса для доступа к Google API
        author = self.user_repo.get(db, survey.author_id)
        if not author or not author.google_access_token:
            raise ValidationException("Survey author doesn't have Google access")
        
        try:
            # Создать Google Forms сервис
            forms_service = get_google_forms_service(author.google_access_token)
            
            # Получить ID формы из URL
            form_id = GoogleFormsService.extract_form_id_from_url(survey.google_form_url)
            if not form_id:
                raise ValidationException("Invalid Google Form URL")
            
            # Получить все ответы из Google Forms
            all_google_responses = []
            next_page_token = None
            
            while True:
                response_data = await forms_service.get_form_responses(
                    form_id, next_page_token
                )
                
                google_responses = response_data.get("responses", [])
                all_google_responses.extend(google_responses)
                
                next_page_token = response_data.get("next_page_token")
                if not next_page_token:
                    break
            
            # Синхронизировать ответы
            synced_count = 0
            new_responses = []
            
            for google_response in all_google_responses:
                google_response_id = google_response.get("responseId")
                
                if not google_response_id:
                    continue
                
                # Проверить, есть ли уже такой ответ
                existing_response = self.response_repo.get_by_google_response_id(
                    db, google_response_id
                )
                
                if not existing_response:
                    # Попытаться найти пользователя по email (если форма собирает email)
                    respondent_id = None
                    if survey.collects_emails:
                        respondent_id = await self._find_respondent_by_email(
                            db, google_response
                        )
                    
                    # Создать новый ответ
                    response_obj = self.response_repo.create_from_google_response(
                        db, survey_id, google_response, respondent_id
                    )
                    new_responses.append(response_obj)
                
                synced_count += 1
            
            # Обновить счетчик ответов в опросе
            total_responses = self.response_repo.count_responses_by_survey(db, survey_id)
            survey.total_responses = total_responses
            survey.last_synced_at = datetime.now(timezone.utc)
            db.commit()
            
            logger.info(f"Synced {len(new_responses)} new responses for survey {survey_id}")
            
            return SyncResponse(
                survey_id=survey_id,
                synced_responses=synced_count,
                new_responses=len(new_responses),
                total_responses=total_responses,
                last_sync_at=survey.last_synced_at
            )
            
        except GoogleAPIException as e:
            logger.error(f"Google API error during sync for survey {survey_id}: {e}")
            raise ValidationException(f"Failed to sync responses: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during sync for survey {survey_id}: {e}")
            raise ValidationException(f"Sync failed: {str(e)}")
    
    async def _find_respondent_by_email(
        self, 
        db: Session, 
        google_response: Dict[str, Any]
    ) -> Optional[int]:
        """Найти ID пользователя по email из ответа Google Forms"""
        try:
            # В Google Forms email обычно хранится в поле respondentEmail
            respondent_email = google_response.get("respondentEmail")
            
            if not respondent_email:
                # Попытаться найти в ответах на вопросы
                answers = google_response.get("answers", {})
                for question_id, answer_data in answers.items():
                    text_answers = answer_data.get("textAnswers", {})
                    if text_answers and text_answers.get("answers"):
                        for answer in text_answers["answers"]:
                            text = answer.get("value", "")
                            # Простая проверка на email
                            if "@" in text and "." in text:
                                respondent_email = text
                                break
                        if respondent_email:
                            break
            
            if respondent_email:
                user = self.user_repo.get_by_email(db, respondent_email)
                return user.id if user else None
            
            return None
            
        except Exception as e:
            logger.warning(f"Could not find respondent email: {e}")
            return None
    
    async def sync_all_active_surveys(self, db: Session) -> List[SyncResponse]:
        """Синхронизировать все активные опросы"""
        active_surveys = self.survey_repo.get_active_surveys(db)
        sync_results = []
        
        for survey in active_surveys:
            try:
                result = await self.sync_survey_responses(db, survey.id)
                sync_results.append(result)
            except Exception as e:
                logger.error(f"Failed to sync survey {survey.id}: {e}")
                # Продолжаем синхронизацию других опросов
                continue
        
        return sync_results
    
    def get_sync_status(self, db: Session, survey_id: int) -> Dict[str, Any]:
        """Получить статус синхронизации опроса"""
        survey = self.survey_repo.get(db, survey_id)
        if not survey:
            raise ValidationException("Survey not found")
        
        stats = self.response_repo.get_response_statistics(db, survey_id)
        
        return {
            "survey_id": survey_id,
            "last_synced_at": survey.last_synced_at,
            "total_responses": stats["total_responses"],
            "last_response_at": stats["last_response_at"],
            "sync_needed": True  # Можно добавить логику определения необходимости синхронизации
        }


# Создаем экземпляр сервиса
survey_sync_service = SurveySyncService()