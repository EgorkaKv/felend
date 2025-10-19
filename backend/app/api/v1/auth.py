from fastapi import APIRouter, Depends, status
from app.api.deps import get_auth_service
from app.schemas import UserRegister, UserLogin, Token, TokenRefresh, ErrorResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", 
    response_model=Token, 
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        409: {"model": ErrorResponse, "description": "User already exists"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def register(user_data: UserRegister, auth_service=Depends(get_auth_service)):
    """Register a new user"""
    user = auth_service.register_user(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
    )
    access_token, refresh_token = auth_service.create_tokens(user)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=1800,  # 30 minutes
    )


@router.post(
    "/login", 
    response_model=Token,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def login(credentials: UserLogin, auth_service=Depends(get_auth_service)):
    """Вход в систему"""
    user = auth_service.authenticate_user(
        email=credentials.email, password=credentials.password
    )
    access_token, refresh_token = auth_service.create_tokens(user)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=1800,  # 30 minutes
    )


@router.post(
    "/refresh", 
    response_model=Token,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Invalid refresh token"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def refresh_token(
    token_data: TokenRefresh, auth_service=Depends(get_auth_service)
):
    """Обновление access токена"""
    access_token, refresh_token = auth_service.refresh_access_token(
        refresh_token=token_data.refresh_token
    )
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=1800,  # 30 minutes
    )
