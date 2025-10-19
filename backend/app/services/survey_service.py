from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import re
from app.models import GoogleAccount, Survey, SurveyStatus
from app.repositories.survey_repository import SurveyRepository, survey_repository
from app.repositories.user_repository import UserRepository, user_repository
from app.services.google_accounts_service import GoogleAccountsService
from app.schemas import (
    GoogleForm,
    SurveyCreate,
    SurveyUpdate,
    SurveyListItem,
    SurveyDetail,
    MySurveyDetail,
)
from app.core.exceptions import (
    SurveyNotFoundException,
    AuthorizationException,
    SurveyValidationException,
    UserNotFoundException,
    ValidationException,
    InsufficientBalanceException,
)
from app.services.google_forms_service import GoogleFormsService


class SurveyService:
    def __init__(self, db: Session):
        self.survey_repo: SurveyRepository = survey_repository
        self.user_repo: UserRepository = user_repository
        self.google_accounts_service = GoogleAccountsService(db)
        self.db = db

    async def create_survey(
        self,
        survey_data: SurveyCreate,
        author_id: int,
        forms_service: GoogleFormsService,
    ) -> Survey:
        """Создать новый опрос"""

        form: GoogleForm = await forms_service.validate_form_access(
            str(survey_data.google_form_url)
        )

        if not form.settings.collect_emails:
            raise SurveyValidationException(
                "The Google Form must be set to collect email addresses. Current collect email settings: "
                + str(form.settings.emailCollectionType),
                form.formId,
            )

        author = self.user_repo.get(self.db, author_id)
        if not author:
            raise UserNotFoundException(user_id=author_id)

        if author.balance < survey_data.reward_per_response:
            raise InsufficientBalanceException(
                survey_data.reward_per_response, author.balance, author_id
            )

        survey = Survey(
            title=form.info.title,
            description=form.info.description,
            google_account_id=survey_data.google_account_id,
            google_form_id=form.formId,
            google_form_url=str(survey_data.google_form_url),
            questions_count=len(form.items),
            question_types={},
            reward_per_response=survey_data.reward_per_response,
            status=SurveyStatus.ACTIVE,
            responses_needed=survey_data.responses_needed,
            max_responses_per_user=survey_data.max_responses_per_user,
        )

        # FIXME: вызов репозитория, а не базы напрямую
        self.db.add(survey)
        self.db.commit()
        self.db.refresh(survey)
        return survey

    def get_surveys_feed(
        self, current_user_id: Optional[int] = None, skip: int = 0, limit: int = 50
    ) -> List[SurveyListItem]:
        """Получить ленту опросов"""

        surveys = self.survey_repo.get_active_surveys(
            self.db, skip, limit, current_user_id
        )

        result = []
        for survey in surveys:
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
                author_name=survey.google_account.name,  # Используем связь с GoogleAccount
                reward_per_response=survey.reward_per_response,
                total_responses=survey.total_responses,
                responses_needed=survey.responses_needed,
                questions_count=survey.questions_count,
                can_participate=can_participate,
                my_responses_count=my_responses_count,
            )
            result.append(survey_item)
        return result

    def _get_google_account_for_user(
        self, user_id: int, google_account_id: Optional[int] = None
    ) -> GoogleAccount:
        """Получить Google аккаунт пользователя по логике:
        - Если google_account_id указан, проверить что он принадлежит пользователю
        - Если не указан, взять primary_google_account пользователя
        """

        if google_account_id:
            # Проверяем что аккаунт принадлежит пользователю
            google_account = self.google_accounts_service.check_user_google_account(
                user_id, google_account_id
            )
            if not google_account:
                raise AuthorizationException(
                    "Google account does not belong to user or is not active"
                )
            return google_account
        else:
            # Используем primary аккаунт
            google_account = self.google_accounts_service.get_primary_google_account(
                user_id
            )
            if not google_account:
                raise ValidationException("User has no primary Google account")
            return google_account

    def get_survey_detail(
        self, survey_id: int, current_user_id: Optional[int] = None
    ) -> SurveyDetail:
        """Получить детали опроса"""
        survey = self.survey_repo.get_with_author(self.db, survey_id)
        if not survey:
            raise SurveyNotFoundException(survey_id)
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
            created_at=survey.created_at,
        )

    def get_my_surveys(
        self,
        user_id: int,
        google_account_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[MySurveyDetail]:
        """Получить мои опросы"""

        google_account = self._get_google_account_for_user(user_id, google_account_id)

        surveys = self.survey_repo.get_user_surveys(
            self.db, google_account.id, skip, limit
        )

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
                created_at=survey.created_at,
            )
            result.append(my_survey)
        return result

    def get_my_survey_detail(self, survey_id: int, user_id: int) -> MySurveyDetail:
        """Получить детали моего опроса"""
        survey = self.survey_repo.get(self.db, survey_id)
        if not survey:
            raise SurveyNotFoundException(survey_id)
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
            created_at=survey.created_at,
        )

    def update_survey(
        self, survey_id: int, survey_update: SurveyUpdate, user_id: int
    ) -> Survey:
        """Обновить опрос"""
        survey = self.survey_repo.get(self.db, survey_id)
        if not survey:
            raise SurveyNotFoundException(survey_id)
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
            raise SurveyNotFoundException(survey_id)
        if survey.author_id != user_id:
            raise AuthorizationException("You are not the author of this survey")
        if survey.total_responses > 0:
            raise ValidationException("Cannot delete survey with responses")
        self.survey_repo.delete(self.db, survey_id)
        return True
