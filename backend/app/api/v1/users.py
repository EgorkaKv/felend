from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, get_current_active_user, get_user_service
from app.schemas import UserProfile, UserUpdate, TransactionItem
from app.models import User, BalanceTransaction
from app.services.user_service import user_service


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Получить свой профиль"""
    return UserProfile.model_validate(current_user)



@router.put("/me", response_model=UserProfile)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service = Depends(get_user_service)
):
    """Обновить свой профиль"""
    updated_user = user_service.update_profile(current_user, user_update)
    return UserProfile.model_validate(updated_user)


# Получить историю транзакций через сервис
@router.get("/me/transactions", response_model=List[TransactionItem])
async def get_my_transactions(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    user_service = Depends(get_user_service)
):
    """Получить историю транзакций"""
    return user_service.get_transactions(current_user, skip=skip, limit=limit)