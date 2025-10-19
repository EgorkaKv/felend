from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_
from app.models import Survey, User, SurveyResponse, SurveyStatus
from app.repositories.base_repository import BaseRepository
from app.schemas import SurveyCreate, SurveyUpdate
from app.core.exceptions import SurveyNotFoundException


class SurveyRepository(BaseRepository[Survey, SurveyCreate, SurveyUpdate]):
    def __init__(self):
        super().__init__(Survey)

    def get_active_surveys(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 50,
        current_user_id: Optional[int] = None
    ) -> List[Survey]:
        """Получить список активных опросов для ленты"""
        query = (
            db.query(Survey)
            # .join(User, Survey.author_id == User.id)
            .filter(Survey.status == SurveyStatus.ACTIVE)
            .order_by(desc(Survey.created_at))
        )
        
        return query.offset(skip).limit(limit).all()

    def get_user_surveys(
        self, 
        db: Session,
        google_account_id: int, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[Survey]:
        """Получить опросы конкретного пользователя"""
        return (
            db.query(Survey)
            .filter(Survey.google_account_id == google_account_id)
            .order_by(desc(Survey.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_google_form_id(self, db: Session, google_form_id: str) -> Optional[Survey]:
        """Получить опрос по Google Form ID"""
        return db.query(Survey).filter(Survey.google_form_id == google_form_id).first()

    def get_with_author(self, db: Session, survey_id: int) -> Optional[Survey]:
        """Получить опрос с информацией об авторе"""
        return (
            db.query(Survey)
            # .join(User, Survey.author_id == User.id)
            .filter(Survey.id == survey_id)
            .first()
        )

    def get_survey_stats(self, db: Session, survey_id: int) -> Dict[str, Any]:
        """Получить статистику по опросу"""
        survey = db.query(Survey).filter(Survey.id == survey_id).first()
        if not survey:
            raise SurveyNotFoundException()

        # Подсчет ответов
        total_responses = (
            db.query(SurveyResponse)
            .filter(SurveyResponse.survey_id == survey_id)
            .count()
        )

        # Подсчет уникальных респондентов
        unique_respondents = (
            db.query(SurveyResponse.respondent_id)
            .filter(SurveyResponse.survey_id == survey_id)
            .distinct()
            .count()
        )

        # Общая стоимость опроса
        total_spent = survey.reward_per_response * total_responses

        return {
            "total_responses": total_responses,
            "unique_respondents": unique_respondents,
            "total_spent": total_spent,
            "responses_needed": survey.responses_needed,
            "completion_rate": (
                (total_responses / survey.responses_needed * 100) 
                if survey.responses_needed else 0
            )
        }

    def get_user_participation_count(
        self, 
        db: Session, 
        survey_id: int, 
        user_id: int
    ) -> int:
        """Подсчитать количество участий пользователя в опросе"""
        return (
            db.query(SurveyResponse)
            .filter(
                and_(
                    SurveyResponse.survey_id == survey_id,
                    SurveyResponse.respondent_id == user_id
                )
            )
            .count()
        )

    def can_user_participate(
        self, 
        db: Session, 
        survey_id: int, 
        user_id: int
    ) -> bool:
        """Проверить может ли пользователь участвовать в опросе"""
        survey = self.get(db, survey_id)
        if not survey or survey.status != SurveyStatus.ACTIVE:
            return False

        # Проверяем что пользователь не автор опроса
        if survey.author_id == user_id:
            return False

        # Проверяем лимит участий
        participation_count = self.get_user_participation_count(db, survey_id, user_id)
        return participation_count < survey.max_responses_per_user

    def update_response_count(self, db: Session, survey_id: int) -> Survey:
        """Обновить счетчик ответов в опросе"""
        survey = self.get(db, survey_id)
        if not survey:
            raise SurveyNotFoundException()

        # Пересчитываем количество ответов
        total_responses = (
            db.query(SurveyResponse)
            .filter(SurveyResponse.survey_id == survey_id)
            .count()
        )

        survey.total_responses = total_responses

        # Автоматически завершаем опрос если достигнут лимит
        if (survey.responses_needed and 
            total_responses >= survey.responses_needed):
            survey.status = SurveyStatus.COMPLETED

        db.commit()
        db.refresh(survey)
        return survey

    def search_surveys(
        self, 
        db: Session, 
        search_query: str, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[Survey]:
        """Поиск опросов по названию или описанию"""
        return (
            db.query(Survey)
            # .join(User, Survey.author_id == User.id)
            .filter(
                and_(
                    Survey.status == SurveyStatus.ACTIVE,
                    or_(
                        Survey.title.ilike(f"%{search_query}%"),
                        Survey.description.ilike(f"%{search_query}%")
                    )
                )
            )
            .order_by(desc(Survey.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_survey(
        self, 
        db: Session, 
        survey_in: SurveyCreate, 
        author_id: int,
        google_account_id: int
    ) -> Survey:
        """Создать новый опрос"""
        survey_data = survey_in.model_dump() if hasattr(survey_in, 'model_dump') else survey_in.dict()
        survey_obj = Survey(
            **survey_data,
            author_id=author_id,
            google_account_id=google_account_id,
            status=SurveyStatus.ACTIVE,
            total_responses=0
        )
        db.add(survey_obj)
        db.commit()
        db.refresh(survey_obj)
        return survey_obj

# Создаем экземпляр репозитория
survey_repository = SurveyRepository()