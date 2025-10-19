"""
Сервис для управления участием в опросах и системой баллов
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging

from app.models import SurveyResponse, BalanceTransaction, TransactionType, SurveyStatus
from app.repositories.survey_repository import survey_repository
from app.repositories.survey_response_repository import survey_response_repository
from app.repositories.user_repository import user_repository
from app.core.exceptions import ValidationException, AuthorizationException, FelendException
from app.schemas import SurveyStartResponse, SurveyVerifyResponse


logger = logging.getLogger(__name__)


class ParticipationService:
    """Сервис для управления участием в опросах"""

    def __init__(self, db: Session):
        self.survey_repo = survey_repository
        self.response_repo = survey_response_repository
        self.user_repo = user_repository
        self.db = db

    def start_participation(self, survey_id: int, user_id: int) -> SurveyStartResponse:
        survey = self.survey_repo.get(self.db, survey_id)
        if not survey:
            raise ValidationException("Survey not found")
        if survey.status != SurveyStatus.ACTIVE:
            raise ValidationException("Survey is not active")
        if (
            survey.responses_needed
            and survey.total_responses >= survey.responses_needed
        ):
            raise ValidationException(
                "Survey has reached the maximum number of responses"
            )
        user = self.user_repo.get(self.db, user_id)
        if not user:
            raise AuthorizationException("User not found")
        can_participate = self.survey_repo.can_user_participate(
            self.db, survey_id, user_id
        )
        if not can_participate:
            raise ValidationException("You cannot participate in this survey")
        existing_response = self.response_repo.get_by_survey_and_respondent(
            self.db, survey_id, user_id
        )
        if existing_response:
            if existing_response.is_verified:
                raise ValidationException("You have already completed this survey")
            else:
                return SurveyStartResponse(
                    google_form_url=survey.google_form_url,
                    respondent_code=user.respondent_code,
                    instructions=f"Continue filling out the form. Use your respondent code: {user.respondent_code}",
                )
        response = SurveyResponse(
            survey_id=survey_id,
            respondent_id=user_id,
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(response)
        self.db.commit()
        logger.info(f"User {user_id} started participation in survey {survey_id}")
        return SurveyStartResponse(
            google_form_url=survey.google_form_url,
            respondent_code=user.respondent_code,
            instructions=f"Please fill out the Google Form and use your respondent code: {user.respondent_code}. After completing the form, return here to claim your reward.",
        )

    def verify_and_reward(
        self,
        survey_id: int,
        user_id: int,
    ) -> SurveyVerifyResponse:
        
        survey = self.survey_repo.get(self.db, survey_id)
        if not survey:
            raise ValidationException("Survey not found")
        
        user = self.user_repo.get(self.db, user_id)
        if not user:
            raise AuthorizationException("User not found")
        
        response = self.response_repo.get_by_survey_and_respondent(
            self.db, survey_id, user_id
        )
        if not response:
            raise ValidationException(
                "You haven't started participation in this survey"
            )
        
        if response.reward_paid:
            raise ValidationException(
                "You have already received the reward for this survey"
            )
        
        author = self.user_repo.get(self.db, survey.author_id)
        if not author:
            raise ValidationException("Survey author not found")
        
        if author.balance < survey.reward_per_response:
            # TODO: сделать опрос неактивным, уведомить автора
            raise ValidationException(
                "Survey author has insufficient balance to pay rewards"
            )
        try:
            user.balance += survey.reward_per_response
            author.balance -= survey.reward_per_response
            participant_transaction = BalanceTransaction(
                user_id=user_id,
                transaction_type=TransactionType.EARNED,
                amount=survey.reward_per_response,
                balance_after=user.balance,
                description=f"Earned {survey.reward_per_response} points for completing survey: {survey.title}",
                related_survey_id=survey_id,
            )
            self.db.add(participant_transaction)
            author_transaction = BalanceTransaction(
                user_id=author.id,
                transaction_type=TransactionType.SPENT,
                amount=-survey.reward_per_response,
                balance_after=author.balance,
                description=f"Paid {survey.reward_per_response} points for response to survey: {survey.title}",
                related_survey_id=survey_id,
            )
            self.db.add(author_transaction)
            response.is_verified = True
            response.reward_paid = True
            response.completed_at = datetime.now(timezone.utc)
            survey.total_responses += 1
            if (
                survey.responses_needed
                and survey.total_responses >= survey.responses_needed
            ):
                survey.status = SurveyStatus.COMPLETED
                logger.info(f"Survey {survey_id} completed - reached target responses")
            self.db.commit()
            logger.info(
                f"User {user_id} completed survey {survey_id} and earned {survey.reward_per_response} points"
            )
            return SurveyVerifyResponse(
                verified=True,
                reward_earned=survey.reward_per_response,
                new_balance=user.balance,
                message=f"Congratulations! You earned {survey.reward_per_response} points. Your new balance is {user.balance} points.",
            )
        except FelendException as e:
            self.db.rollback()
            logger.error(
                f"Error processing reward for user {user_id} in survey {survey_id}: {e}"
            )
            raise ValidationException("Failed to process reward. Please try again.")

    def get_user_participation_status(
        self, survey_id: int, user_id: int
    ) -> Dict[str, Any]:
        can_participate = self.survey_repo.can_user_participate(
            self.db, survey_id, user_id
        )
        response = self.response_repo.get_by_survey_and_respondent(
            self.db, survey_id, user_id
        )
        if not response:
            return {
                "status": "not_started",
                "can_participate": can_participate,
                "started_at": None,
                "completed_at": None,
                "reward_earned": 0,
            }
        if response.reward_paid:
            survey = self.survey_repo.get(self.db, survey_id)
            reward_earned = survey.reward_per_response if survey else 0
            return {
                "status": "completed",
                "can_participate": False,
                "started_at": response.started_at,
                "completed_at": response.completed_at,
                "reward_earned": reward_earned,
            }
        return {
            "status": "in_progress",
            "can_participate": False,
            "started_at": response.started_at,
            "completed_at": None,
            "reward_earned": 0,
        }

    def get_user_responses_count(self, survey_id: int, user_id: int) -> int:
        return (
            self.db.query(SurveyResponse)
            .filter(
                SurveyResponse.survey_id == survey_id,
                SurveyResponse.respondent_id == user_id,
                SurveyResponse.is_verified == True,
            )
            .count()
        )
