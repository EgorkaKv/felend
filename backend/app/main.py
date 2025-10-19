from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
import time
import logging
import traceback
import uuid

from app.core.config import settings
from app.core.exceptions import FelendException
from app.schemas import ErrorResponse, ErrorDetail, ValidationErrorResponse, ValidationErrorDetail
from app.api.v1 import (
    auth,
    google_auth,
    users,
    surveys,
    participation,
    google_accounts,
    google_forms,
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Создание FastAPI приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API for the Felend survey exchange platform",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware для логирования запросов и ошибок
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    """
    Middleware для перехвата неожиданных исключений и логирования
    
    - Генерирует уникальный request_id для трейсинга
    - Логирует все входящие запросы и время выполнения
    - Перехватывает неожиданные исключения
    - В dev режиме показывает stack trace, в prod скрывает детали
    - Добавляет структурированное логирование с контекстом
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # Извлекаем дополнительную информацию о запросе
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("User-Agent", "unknown")
    content_type = request.headers.get("Content-Type", "unknown")
    
    # Логируем входящий запрос с контекстом
    logger.info(
        f"[{request_id}] {request.method} {request.url}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url.path),
            "query_params": dict(request.query_params) if request.query_params else {},
            "client_ip": client_ip,
            "user_agent": user_agent,
            "content_type": content_type,
            "event": "request_start"
        }
    )
    
    try:
        response = await call_next(request)
        
        # Логируем успешное завершение
        process_time = time.time() - start_time
        logger.info(
            f"[{request_id}] Completed {response.status_code} in {process_time:.4f}s",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time": process_time,
                "response_size": response.headers.get("content-length", "unknown"),
                "event": "request_completed"
            }
        )
        
        return response
        
    except Exception as exc:
        # Перехватываем все неожиданные исключения
        process_time = time.time() - start_time
        
        # Структурированное логирование ошибки
        logger.error(
            f"[{request_id}] Unhandled {type(exc).__name__}: {exc}",
            extra={
                "request_id": request_id,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "method": request.method,
                "path": str(request.url.path),
                "query_params": dict(request.query_params) if request.query_params else {},
                "client_ip": client_ip,
                "user_agent": user_agent,
                "process_time": process_time,
                "event": "unhandled_exception"
            },
            exc_info=settings.DEBUG  # Добавляем traceback только в DEBUG режиме
        )
        
        # Создаем ответ с ошибкой
        if settings.DEBUG:
            # В dev режиме показываем детали ошибки и stack trace
            error_detail = ErrorDetail(
                message=f"Internal server error: {str(exc)}",
                code="INTERNAL_ERROR", 
                type=type(exc).__name__,
                details={
                    "exception_message": str(exc),
                    "traceback": traceback.format_exc().split('\n'),
                    "request_id": request_id,
                    "process_time": f"{process_time:.4f}s"
                },
                timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                path=str(request.url.path)
            )
        else:
            # В production скрываем детали для безопасности
            error_detail = ErrorDetail(
                message="Internal server error",
                code="INTERNAL_ERROR",
                type="InternalServerError", 
                details={
                    "request_id": request_id  # Оставляем только request_id для debugging
                },
                timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                path=str(request.url.path)
            )
        
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(error=error_detail).model_dump()
        )


# Обработчик кастомных исключений Felend
@app.exception_handler(FelendException)
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


# Обработчик ошибок валидации Pydantic
@app.exception_handler(RequestValidationError)
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


# Обработчик ошибок валидации SQLAlchemy  
@app.exception_handler(IntegrityError)
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


# Подключение роутеров
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(surveys.router, prefix="/api/v1")
app.include_router(google_auth.router, prefix="/api/v1")
app.include_router(google_accounts.router, prefix="/api/v1")
app.include_router(google_forms.router, prefix="/api/v1")
app.include_router(participation.router, prefix="/api/v1")

# Подключаем dev endpoints только в режиме разработки
# if settings.DEBUG:
#     app.include_router(dev.router, prefix="/api/v1")


# Базовые эндпоинты
@app.get("/")
async def root():
    return {"message": "Felend API", "version": settings.VERSION, "status": "running"}


@app.get("/health")
async def health_check():
    """Health check эндпоинт"""
    return {"status": "healthy", "timestamp": time.time()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
