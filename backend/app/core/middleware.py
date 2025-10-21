"""
Middleware для FastAPI приложения
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import time
import logging
import traceback
import uuid

from app.core.config import settings
from app.schemas import ErrorResponse, ErrorDetail


logger = logging.getLogger(__name__)


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
