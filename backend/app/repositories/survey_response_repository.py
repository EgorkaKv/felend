"""
Репозиторий для работы с ответами на опросы
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime

from app.models import SurveyResponse, Survey
from app.repositories.base_repository import BaseRepository
from app.schemas import SurveyResponseCreate, SurveyResponseUpdate


class SurveyResponseRepository(BaseRepository[SurveyResponse, SurveyResponseCreate, SurveyResponseUpdate]):
    def __init__(self):
        super().__init__(SurveyResponse)
    
    def get_by_survey_and_respondent(
        self, 
        db: Session, 
        survey_id: int, 
        respondent_id: int
    ) -> Optional[SurveyResponse]:
        """Получить ответ пользователя на конкретный опрос"""
        return db.query(SurveyResponse).filter(
            and_(
                SurveyResponse.survey_id == survey_id,
                SurveyResponse.respondent_id == respondent_id
            )
        ).first()
    
    def get_by_survey(self, db: Session, survey_id: int) -> List[SurveyResponse]:
        """Получить все ответы на опрос"""
        return db.query(SurveyResponse).filter(
            SurveyResponse.survey_id == survey_id
        ).order_by(desc(SurveyResponse.submitted_at)).all()
    
    def get_completed_responses(
        self, 
        db: Session, 
        survey_id: int
    ) -> List[SurveyResponse]:
        """Получить завершенные ответы на опрос"""
        return db.query(SurveyResponse).filter(
            SurveyResponse.survey_id == survey_id,
            SurveyResponse.is_verified == True
        ).order_by(SurveyResponse.completed_at.desc()).all()
    
    def get_user_completed_responses_count(
        self, 
        db: Session, 
        user_id: int
    ) -> int:
        """Получить количество завершенных ответов пользователя"""
        return db.query(SurveyResponse).filter(
            SurveyResponse.respondent_id == user_id,
            SurveyResponse.is_verified == True
        ).count()
    
    def create_participation_record(
        self, 
        db: Session, 
        survey_id: int,
        respondent_id: int
    ) -> SurveyResponse:
        """Создать запись об участии в опросе"""
        response_obj = SurveyResponse(
            survey_id=survey_id,
            respondent_id=respondent_id,
            started_at=datetime.utcnow()
        )
        
        db.add(response_obj)
        db.commit()
        db.refresh(response_obj)
        
        return response_obj
    
    def mark_as_completed(
        self, 
        db: Session, 
        response_id: int
    ) -> SurveyResponse:
        """Отметить участие как завершенное"""
        response = self.get(db, response_id)
        if not response:
            raise ValueError("Response not found")
        
        response.is_verified = True
        response.reward_paid = True
        response.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(response)
        
        return response
    
    def get_user_responses(
        self, 
        db: Session, 
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[SurveyResponse]:
        """Получить ответы пользователя"""
        return db.query(SurveyResponse).filter(
            SurveyResponse.respondent_id == user_id
        ).order_by(desc(SurveyResponse.submitted_at)).offset(offset).limit(limit).all()
    
    def count_responses_by_survey(self, db: Session, survey_id: int) -> int:
        """Подсчитать количество ответов на опрос"""
        return db.query(SurveyResponse).filter(
            SurveyResponse.survey_id == survey_id
        ).count()
    
    def get_response_statistics(self, db: Session, survey_id: int) -> Dict[str, Any]:
        """Получить статистику ответов на опрос"""
        total_responses = self.count_responses_by_survey(db, survey_id)
        completed_responses = db.query(SurveyResponse).filter(
            SurveyResponse.survey_id == survey_id,
            SurveyResponse.is_verified == True
        ).count()
        
        # Получаем последний завершенный ответ
        last_response = db.query(SurveyResponse).filter(
            SurveyResponse.survey_id == survey_id,
            SurveyResponse.is_verified == True
        ).order_by(desc(SurveyResponse.completed_at)).first()
        
        return {
            "total_responses": total_responses,
            "completed_responses": completed_responses,
            "last_response_at": last_response.completed_at if last_response else None,
            "survey_id": survey_id
        }


# Создаем экземпляр репозитория
survey_response_repository = SurveyResponseRepository()