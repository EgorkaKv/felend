from fastapi import APIRouter, Depends, status
from app.api.deps import get_auth_service, get_db
from app.schemas import (
    UserRegister, UserLogin, Token, TokenRefresh, ErrorResponse,
    RegisterResponse, RequestVerificationCode, VerificationCodeResponse,
    VerifyEmail, EmailVerifiedResponse, UserProfile,
    ForgotPasswordRequest, ForgotPasswordResponse,
    PasswordResetRequest, PasswordResetResponse
)
from app.services.email_verification_service import EmailVerificationService
from app.services.password_reset_service import PasswordResetService
from sqlalchemy.orm import Session


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", 
    response_model=RegisterResponse, 
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        409: {"model": ErrorResponse, "description": "User already exists"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def register(user_data: UserRegister, auth_service=Depends(get_auth_service)):
    """
    Register a new user
    
    Creates an inactive user account and returns a verification token.
    User must verify their email to activate the account.
    """
    user, verification_token = auth_service.register_user(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
    )
    
    return RegisterResponse(
        verification_token=verification_token,
        email=user.email,
        message="Registration successful. Please verify your email to activate your account."
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


@router.post(
    "/request-verification-code",
    response_model=VerificationCodeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid verification token"},
        404: {"model": ErrorResponse, "description": "Verification not found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def request_verification_code(
    request: RequestVerificationCode,
    db: Session = Depends(get_db)
):
    """
    Request a verification code
    
    Sends a 6-digit verification code to the user's email.
    Can only be requested once per 60 seconds.
    """
    verification_service = EmailVerificationService(db)
    message, masked_email = verification_service.request_verification_code(request.verification_token)
    
    return VerificationCodeResponse(
        success=True,
        message=message,
        email_masked=masked_email
    )


@router.post(
    "/verify-email",
    response_model=EmailVerifiedResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid verification code"},
        404: {"model": ErrorResponse, "description": "Verification not found"},
        410: {"model": ErrorResponse, "description": "Verification expired or used"},
        429: {"model": ErrorResponse, "description": "Too many attempts"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def verify_email(
    request: VerifyEmail,
    db: Session = Depends(get_db)
):
    """
    Verify email with code
    
    Verifies the email address using the 6-digit code.
    Activates the user account and returns authentication tokens.
    Maximum 5 attempts allowed.
    """
    verification_service = EmailVerificationService(db)
    access_token, refresh_token, user_dict = verification_service.verify_email(
        verification_token=request.verification_token,
        code=request.code
    )
    
    return EmailVerifiedResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=1800,
        user=UserProfile(**user_dict)
    )


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid email format"},
        429: {"model": ErrorResponse, "description": "Too many requests"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset code
    
    Sends a 6-digit code to the user's email for password reset.
    Rate limited to 3 requests per hour per user.
    Code expires in 15 minutes.
    """
    password_reset_service = PasswordResetService(db)
    message, masked_email = password_reset_service.request_password_reset(request.email)
    
    return ForgotPasswordResponse(
        success=True,
        message=message,
        email_masked=masked_email
    )


@router.post(
    "/reset-password",
    response_model=PasswordResetResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid code or request"},
        404: {"model": ErrorResponse, "description": "User not found or no active reset request"},
        410: {"model": ErrorResponse, "description": "Reset request expired"},
        429: {"model": ErrorResponse, "description": "Too many attempts"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def reset_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password with verification code
    
    Verifies the 6-digit code and resets the user's password.
    Maximum 5 attempts allowed per reset request.
    """
    password_reset_service = PasswordResetService(db)
    user_data = password_reset_service.reset_password(
        email=request.email,
        code=request.code,
        new_password=request.new_password
    )
    
    return PasswordResetResponse(
        success=True,
        message="Password successfully reset",
        user=user_data
    )
