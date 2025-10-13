from typing import List, Dict, Any, Optional
from fastapi import Depends
from sqlalchemy.orm import Session
from urllib.parse import urlparse
import re
from app.api.deps import get_google_accounts_service
from app.models import Survey, SurveyStatus
from app.repositories.survey_repository import survey_repository
from app.repositories.user_repository import user_repository
from app.schemas import SurveyCreate, SurveyUpdate, SurveyListItem, SurveyDetail, MySurveyDetail
from app.core.exceptions import (
    SurveyNotFoundException, 
    AuthorizationException, 
    ValidationException,
    InsufficientBalanceException
)


class SurveyService:
    def __init__(self, db: Session):
        self.survey_repo = survey_repository
        self.user_repo = user_repository
        self.db = db

    def validate_google_form_url(self, url: str) -> Dict[str, Any]:
        """Валидация и извлечение данных из Google Form URL - базовая проверка формата"""
        # Регулярное выражение для Google Forms URL
        google_forms_pattern = r'https://docs\.google\.com/forms/d/([a-zA-Z0-9-_]+)'
        short_url_pattern = r'https://forms\.gle/([a-zA-Z0-9-_]+)'
        
        form_id = None
        
        # Проверяем длинный URL
        match = re.match(google_forms_pattern, url)
        if match:
            form_id = match.group(1)
        else:
            # Проверяем короткий URL
            match = re.match(short_url_pattern, url)
            if match:
                form_id = match.group(1)
        
        if not form_id:
            raise ValidationException("Invalid Google Forms URL format")
        
        return {
            "google_form_id": form_id,
            "google_form_url": url,
            "is_valid": True
        }
    
    async def validate_google_form_access(
        self, url: str, access_token: str, google_forms_service = Depends(get_google_accounts_service)
    ) -> Dict[str, Any]:
        """Валидировать доступ к Google Forms через API"""
        
        # Извлечь ID формы из URL
        form_id = google_forms_service.extract_form_id_from_url(url)
        if not form_id:
            raise ValidationException("Invalid Google Forms URL format")
        
        # Создать сервис и проверить доступ
        forms_service = google_forms_service
        
        try:
            form_info = await forms_service.get_form_info(form_id)
            return {
                "google_form_id": form_id,
                "google_form_url": url,
                "is_valid": True,
                "form_info": form_info
            }
        except Exception as e:
            raise ValidationException(f"Cannot access Google Form: {str(e)}")

    def create_survey(
        self, 
        survey_data: SurveyCreate, 
        author_id: int
    ) -> Survey:
        """Создать новый опрос"""
        # Валидируем Google Form URL
        form_info = self.validate_google_form_url(str(survey_data.google_form_url))
        existing_survey = self.survey_repo.get_by_google_form_id(
            self.db, form_info["google_form_id"]
        )
        if existing_survey:
            raise ValidationException("This Google Form is already used in another survey")
        author = self.user_repo.get(self.db, author_id)
        if not author:
            raise AuthorizationException("User not found")
        estimated_cost = (
            survey_data.reward_per_response * survey_data.responses_needed
            if survey_data.responses_needed
            else survey_data.reward_per_response * 10
        )
        if author.balance < estimated_cost:
            raise InsufficientBalanceException(estimated_cost, author.balance)
        survey = Survey(
            title=survey_data.title,
            description=survey_data.description,
            author_id=author_id,
            google_form_id=form_info["google_form_id"],
            google_form_url=form_info["google_form_url"],
            reward_per_response=survey_data.reward_per_response,
            responses_needed=survey_data.responses_needed,
            max_responses_per_user=survey_data.max_responses_per_user,
            collects_emails=survey_data.collects_emails,
            status=SurveyStatus.DRAFT,
            questions_count=0,
            question_types={}
        )
        self.db.add(survey)
        self.db.commit()
        self.db.refresh(survey)
        return survey

    def get_surveys_feed(
        self, 
        current_user_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 50
    ) -> List[SurveyListItem]:
        """Получить ленту опросов"""
        surveys = self.survey_repo.get_active_surveys(self.db, skip, limit, current_user_id)
        result = []
        for survey in surveys:
            author = self.user_repo.get(self.db, survey.author_id)
            can_participate = False
            my_responses_count = 0
            if current_user_id:
                can_participate = self.survey_repo.can_user_participate(
                    self.db, survey.id, current_user_id
                )
                my_responses_count = self.survey_repo.get_user_participation_count(
                    self.db, survey.id, current_user_id
                )
            survey_item = SurveyListItem(
                id=survey.id,
                title=survey.title,
                description=survey.description,
                author_name=author.full_name if author else "Unknown",
                reward_per_response=survey.reward_per_response,
                total_responses=survey.total_responses,
                responses_needed=survey.responses_needed,
                questions_count=survey.questions_count,
                can_participate=can_participate,
                my_responses_count=my_responses_count
            )
            result.append(survey_item)
        return result

    def get_survey_detail(
        self, 
        survey_id: int, 
        current_user_id: Optional[int] = None
    ) -> SurveyDetail:
        """Получить детали опроса"""
        survey = self.survey_repo.get_with_author(self.db, survey_id)
        if not survey:
            raise SurveyNotFoundException()
        author = self.user_repo.get(self.db, survey.author_id)
        can_participate = False
        my_responses_count = 0
        if current_user_id:
            can_participate = self.survey_repo.can_user_participate(
                self.db, survey.id, current_user_id
            )
            my_responses_count = self.survey_repo.get_user_participation_count(
                self.db, survey.id, current_user_id
            )
        return SurveyDetail(
            id=survey.id,
            title=survey.title,
            description=survey.description,
            author_name=author.full_name if author else "Unknown",
            reward_per_response=survey.reward_per_response,
            total_responses=survey.total_responses,
            responses_needed=survey.responses_needed,
            questions_count=survey.questions_count,
            google_form_url=survey.google_form_url,
            collects_emails=survey.collects_emails,
            max_responses_per_user=survey.max_responses_per_user,
            can_participate=can_participate,
            my_responses_count=my_responses_count,
            created_at=survey.created_at
        )

    def get_my_surveys(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[MySurveyDetail]:
        """Получить мои опросы"""
        surveys = self.survey_repo.get_user_surveys(self.db, user_id, skip, limit)
        result = []
        for survey in surveys:
            stats = self.survey_repo.get_survey_stats(self.db, survey.id)
            my_survey = MySurveyDetail(
                id=survey.id,
                title=survey.title,
                description=survey.description,
                status=survey.status,
                google_form_url=survey.google_form_url,
                reward_per_response=survey.reward_per_response,
                responses_needed=survey.responses_needed,
                max_responses_per_user=survey.max_responses_per_user,
                total_responses=survey.total_responses,
                total_spent=stats["total_spent"],
                questions_count=survey.questions_count,
                collects_emails=survey.collects_emails,
                created_at=survey.created_at
            )
            result.append(my_survey)
        return result

    def get_my_survey_detail(
        self, 
        survey_id: int, 
        user_id: int
    ) -> MySurveyDetail:
        """Получить детали моего опроса"""
        survey = self.survey_repo.get(self.db, survey_id)
        if not survey:
            raise SurveyNotFoundException()
        if survey.author_id != user_id:
            raise AuthorizationException("You are not the author of this survey")
        stats = self.survey_repo.get_survey_stats(self.db, survey.id)
        return MySurveyDetail(
            id=survey.id,
            title=survey.title,
            description=survey.description,
            status=survey.status,
            google_form_url=survey.google_form_url,
            reward_per_response=survey.reward_per_response,
            responses_needed=survey.responses_needed,
            max_responses_per_user=survey.max_responses_per_user,
            total_responses=survey.total_responses,
            total_spent=stats["total_spent"],
            questions_count=survey.questions_count,
            collects_emails=survey.collects_emails,
            created_at=survey.created_at
        )

    def update_survey(
        self, 
        survey_id: int, 
        survey_update: SurveyUpdate, 
        user_id: int
    ) -> Survey:
        """Обновить опрос"""
        survey = self.survey_repo.get(self.db, survey_id)
        if not survey:
            raise SurveyNotFoundException()
        if survey.author_id != user_id:
            raise AuthorizationException("You are not the author of this survey")
        if survey.status == SurveyStatus.ACTIVE and survey.total_responses > 0:
            allowed_fields = {"status", "responses_needed"}
            update_data = survey_update.model_dump(exclude_unset=True)
            if not set(update_data.keys()).issubset(allowed_fields):
                raise ValidationException("Cannot modify active survey with responses")
        updated_survey = self.survey_repo.update(self.db, survey, survey_update)
        return updated_survey

    def delete_survey(self, survey_id: int, user_id: int) -> bool:
        """Удалить опрос"""
        survey = self.survey_repo.get(self.db, survey_id)
        if not survey:
            raise SurveyNotFoundException()
        if survey.author_id != user_id:
            raise AuthorizationException("You are not the author of this survey")
        if survey.total_responses > 0:
            raise ValidationException("Cannot delete survey with responses")
        self.survey_repo.delete(self.db, survey_id)
        return True
