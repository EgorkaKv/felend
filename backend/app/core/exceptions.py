from fastapi import HTTPException, status


class FelendException(HTTPException):
    """Base exception for the Felend application"""
    pass


class AuthenticationException(FelendException):
    """Authentication errors"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class AuthorizationException(FelendException):
    """Authorization errors"""
    def __init__(self, detail: str = "Access denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ValidationException(FelendException):
    """Validation errors"""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class NotFoundException(FelendException):
    """Resource not found"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictException(FelendException):
    """Data conflict"""
    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


# Специфичные исключения для Felend

class UserNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("User not found")


class UserAlreadyExistsException(ConflictException):
    def __init__(self):
        super().__init__("User with this email already exists")


class GoogleAPIException(FelendException):
    def __init__(self, message: str = "Google API error"):
        super().__init__(status_code=502, detail=message)


class InvalidCredentialsException(AuthenticationException):
    def __init__(self):
        super().__init__("Invalid email or password")


class InsufficientBalanceException(FelendException):
    def __init__(self, required: int, current: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Required: {required}, Current: {current}"
        )


class SurveyNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Survey not found")


class AlreadyParticipatedException(ConflictException):
    def __init__(self):
        super().__init__("You have already participated in this survey maximum number of times")


class GoogleFormsException(FelendException):
    def __init__(self, detail: str = "Google Forms API error"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)


class SurveyValidationException(ValidationException):
    def __init__(self, detail: str):
        super().__init__(f"Survey validation error: {detail}")


class ResponseVerificationException(FelendException):
    def __init__(self, detail: str = "Response verification failed"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)