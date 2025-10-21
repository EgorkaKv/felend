"""
Обработчики исключений для FastAPI приложения
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
import logging

from app.core.config import settings
from app.core.exceptions import FelendException
from app.schemas import ErrorResponse, ErrorDetail, ValidationErrorResponse, ValidationErrorDetail


logger = logging.getLogger(__name__)


async def felend_exception_handler(request: Request, exc: FelendException):
    """Обработка всех FelendException с единым форматом"""
    error_detail = ErrorDetail(
        message=exc.message,
        code=exc.error_code,
        type=type(exc).__name__,
        details=exc.context,
        timestamp=exc.timestamp,
        path=str(request.url.path)
    )
    
    logger.warning(
        f"FelendException: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "path": str(request.url.path),
            "status_code": exc.status_code,
            "context": exc.context
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=error_detail).model_dump()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработка ошибок валидации с детальной информацией"""
    
    error_detail = ValidationErrorDetail(
        message="Validation error",
        code="VALIDATION001",
        type="ValidationError",
        details=list(exc.errors()),
        timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        path=str(request.url.path)
    )
    
    logger.warning(
        f"Validation error: {len(exc.errors())} errors",
        extra={
            "path": str(request.url.path),
            "errors": exc.errors()
        }
    )
    
    return JSONResponse(
        status_code=422,
        content=ValidationErrorResponse(error=error_detail).model_dump()
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Обработка ошибок целостности БД"""
    logger.error(f"Database integrity error: {exc}")
    
    # Попытаемся определить тип ошибки по сообщению
    error_message = "Data integrity violation"
    error_code = "DATABASE001"
    
    if "UNIQUE constraint failed" in str(exc.orig):
        error_message = "Resource already exists"
        error_code = "DATABASE002"
    elif "FOREIGN KEY constraint failed" in str(exc.orig):
        error_message = "Referenced resource not found"
        error_code = "DATABASE003"
        
    error_detail = ErrorDetail(
        message=error_message,
        code=error_code,
        type="IntegrityError",
        details={"original_error": str(exc.orig)} if settings.DEBUG else {},
        timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        path=str(request.url.path)
    )
    
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(error=error_detail).model_dump()
    )
