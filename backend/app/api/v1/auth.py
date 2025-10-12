from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_auth_service
from app.schemas import UserRegister, UserLogin, Token, TokenRefresh
from app.services.auth_service import auth_service
from app.core.exceptions import UserAlreadyExistsException, InvalidCredentialsException


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    auth_service = Depends(get_auth_service)
):
    """Register a new user"""
    try:
        user = auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        access_token, refresh_token = auth_service.create_tokens(user)
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1800  # 30 minutes
        )
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    auth_service = Depends(get_auth_service)
):
    """Вход в систему"""
    try:
        user = auth_service.authenticate_user(
            email=credentials.email,
            password=credentials.password
        )
        access_token, refresh_token = auth_service.create_tokens(user)
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1800  # 30 minutes
        )
    except InvalidCredentialsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    auth_service = Depends(get_auth_service)
):
    """Обновление access токена"""
    try:
        access_token, refresh_token = auth_service.refresh_access_token(
            refresh_token=token_data.refresh_token
        )
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1800  # 30 minutes
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
