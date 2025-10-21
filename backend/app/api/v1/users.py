from fastapi import APIRouter, Depends
from typing import List
from app.api.deps import get_current_active_user, get_user_service
from app.schemas import UserProfile, UserUpdate, TransactionItem, ErrorResponse
from app.models import User
import logging

from app.services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me", 
    response_model=UserProfile,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def get_my_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return UserProfile.model_validate(current_user.to_dict())


@router.put(
    "/me", 
    response_model=UserProfile,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """Update current user profile"""
    updated_user = user_service.update_profile(current_user, user_update)
    return UserProfile.model_validate(updated_user, from_attributes=True)


# Получить историю транзакций через сервис
@router.get(
    "/me/transactions", 
    response_model=List[TransactionItem],
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def get_my_transactions(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    user_service=Depends(get_user_service),
):
    """Get user transaction history"""
    return user_service.get_transactions(current_user, skip=skip, limit=limit)
