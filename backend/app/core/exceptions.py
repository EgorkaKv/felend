"""
Система обработки исключений для Felend API
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Union
from fastapi import status


# Коды ошибок по модулям
class ErrorCodes:
    """Централизованные коды ошибок"""
    
    # Authentication & Authorization
    INVALID_CREDENTIALS = "AUTH001"
    TOKEN_EXPIRED = "AUTH002"
    TOKEN_INVALID = "AUTH003"
    INSUFFICIENT_PERMISSIONS = "AUTH004"
    USER_INACTIVE = "AUTH005"
    
    # User Management
    USER_NOT_FOUND = "USER001"
    USER_ALREADY_EXISTS = "USER002"
    INVALID_USER_DATA = "USER003"
    
    # Surveys
    SURVEY_NOT_FOUND = "SURVEY001"
    INSUFFICIENT_BALANCE = "SURVEY002" 
    SURVEY_INACTIVE = "SURVEY003"
    ALREADY_PARTICIPATED = "SURVEY004"
    SURVEY_FULL = "SURVEY005"
    INVALID_SURVEY_DATA = "SURVEY006"
    
    # Google API & Forms
    GOOGLE_FORM_ACCESS_DENIED = "GOOGLE001"
    GOOGLE_API_LIMIT_EXCEEDED = "GOOGLE002"
    GOOGLE_FORM_NOT_FOUND = "GOOGLE003"
    GOOGLE_ACCOUNT_NOT_FOUND = "GOOGLE004"
    GOOGLE_TOKEN_INVALID = "GOOGLE005"
    
    # Validation
    VALIDATION_ERROR = "VALIDATION001"
    MISSING_REQUIRED_FIELD = "VALIDATION002"
    INVALID_FORMAT = "VALIDATION003"
    
    # General
    RESOURCE_NOT_FOUND = "GENERAL001"
    CONFLICT = "GENERAL002"
    INTERNAL_ERROR = "GENERAL003"


class FelendException(Exception):
    """
    Базовое исключение для всех ошибок Felend API
    
    Args:
        message: Человекочитаемое сообщение об ошибке
        status_code: HTTP статус код
        error_code: Уникальный код ошибки для API
        context: Дополнительная контекстная информация
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: int = 500,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or ErrorCodes.INTERNAL_ERROR
        self.context = context or {}
        self.timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование исключения в словарь для JSON ответа"""
        return {
            "message": self.message,
            "code": self.error_code,
            "type": self.__class__.__name__,
            "details": self.context,
            "timestamp": self.timestamp
        }


# === БАЗОВЫЕ ИСКЛЮЧЕНИЯ ПО ТИПАМ ===

class AuthenticationException(FelendException):
    """Ошибки аутентификации (401)"""
    def __init__(self, message: str = "Authentication failed", error_code: str = ErrorCodes.INVALID_CREDENTIALS, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, error_code, context)


class AuthorizationException(FelendException):
    """Ошибки авторизации (403)"""
    def __init__(self, message: str = "Access denied", error_code: str = ErrorCodes.INSUFFICIENT_PERMISSIONS, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, error_code, context)


class ValidationException(FelendException):
    """Ошибки валидации (422)"""
    def __init__(self, message: str = "Validation error", error_code: str = ErrorCodes.VALIDATION_ERROR, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, error_code, context)


class NotFoundException(FelendException):
    """Ресурс не найден (404)"""
    def __init__(self, message: str = "Resource not found", error_code: str = ErrorCodes.RESOURCE_NOT_FOUND, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, error_code, context)


class ConflictException(FelendException):
    """Конфликт данных (409)"""
    def __init__(self, message: str = "Conflict", error_code: str = ErrorCodes.CONFLICT, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_409_CONFLICT, error_code, context)


class GoogleAPIException(FelendException):
    """Ошибки внешних API (502/503)"""
    def __init__(self, message: str = "External API error", error_code: str = ErrorCodes.GOOGLE_FORM_ACCESS_DENIED, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_502_BAD_GATEWAY, error_code, context)


# === СПЕЦИФИЧНЫЕ ИСКЛЮЧЕНИЯ ===

# Auth специфичные
class InvalidCredentialsException(AuthenticationException):
    def __init__(self, context: Optional[Dict[str, Any]] = None):
        super().__init__("Invalid email or password", ErrorCodes.INVALID_CREDENTIALS, context)


class TokenExpiredException(AuthenticationException):
    def __init__(self, context: Optional[Dict[str, Any]] = None):
        super().__init__("Token has expired", ErrorCodes.TOKEN_EXPIRED, context)


class InvalidTokenException(AuthenticationException):
    def __init__(self, context: Optional[Dict[str, Any]] = None):
        super().__init__("Invalid or malformed token", ErrorCodes.TOKEN_INVALID, context)


class UserInactiveException(AuthorizationException):
    def __init__(self, user_id: int):
        super().__init__(
            "User account is inactive", 
            ErrorCodes.USER_INACTIVE, 
            {"user_id": user_id}
        )


# User специфичные
class UserNotFoundException(NotFoundException):
    def __init__(self, user_id: Optional[int] = None, email: Optional[str] = None):
        context = {}
        if user_id:
            context["user_id"] = user_id
        if email:
            context["email"] = email
        super().__init__("User not found", ErrorCodes.USER_NOT_FOUND, context)


class UserAlreadyExistsException(ConflictException):
    def __init__(self, email: str):
        super().__init__(
            "User with this email already exists", 
            ErrorCodes.USER_ALREADY_EXISTS, 
            {"email": email}
        )


# Survey специфичные
class SurveyNotFoundException(NotFoundException):
    def __init__(self, survey_id: int):
        super().__init__(
            "Survey not found", 
            ErrorCodes.SURVEY_NOT_FOUND, 
            {"survey_id": survey_id}
        )


class InsufficientBalanceException(ValidationException):
    def __init__(self, required: int, current: int, user_id: int):
        super().__init__(
            f"Insufficient balance. Required: {required}, Current: {current}",
            ErrorCodes.INSUFFICIENT_BALANCE,
            {"required": required, "current": current, "user_id": user_id}
        )


class AlreadyParticipatedException(ConflictException):
    def __init__(self, survey_id: int, user_id: int):
        super().__init__(
            "You have already participated in this survey maximum number of times",
            ErrorCodes.ALREADY_PARTICIPATED,
            {"survey_id": survey_id, "user_id": user_id}
        )


class SurveyValidationException(ValidationException):
    def __init__(self, detail: str, survey_id: Optional[int] = None):
        context = {"validation_detail": detail}
        if survey_id:
            context["survey_id"] = str(survey_id)
        super().__init__(f"Survey validation error: {detail}", ErrorCodes.INVALID_SURVEY_DATA, context)


# Google API специфичные
class GoogleFormNotFoundException(GoogleAPIException):
    def __init__(self, form_id: str):
        super().__init__(
            "Google Form not found or access denied",
            ErrorCodes.GOOGLE_FORM_NOT_FOUND,
            {"form_id": form_id}
        )


class GoogleAccountNotFoundException(NotFoundException):
    def __init__(self, account_id: int, user_id: int):
        super().__init__(
            "Google account not found or access denied",
            ErrorCodes.GOOGLE_ACCOUNT_NOT_FOUND,
            {"account_id": account_id, "user_id": user_id}
        )


class GoogleTokenInvalidException(GoogleAPIException):
    def __init__(self, account_id: int):
        super().__init__(
            "Google token is invalid or expired",
            ErrorCodes.GOOGLE_TOKEN_INVALID,
            {"account_id": account_id}
        )


class ResponseVerificationException(ValidationException):
    def __init__(self, detail: str, survey_id: Optional[int] = None, user_id: Optional[int] = None):
        context = {"verification_detail": detail}
        if survey_id:
            context["survey_id"] = str(survey_id)
        if user_id:
            context["user_id"] = str(user_id)
        super().__init__(f"Response verification failed: {detail}", ErrorCodes.VALIDATION_ERROR, context)


# Alias для обратной совместимости
GoogleFormsException = GoogleAPIException