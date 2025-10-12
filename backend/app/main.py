from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
import time
import logging

from app.core.config import settings
from app.core.exceptions import FelendException
from app.api.v1 import auth
# from app.api.v1 import users, surveys, google, participation
# if settings.DEBUG:
    # from app.api.v1 import dev


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
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Логируем входящий запрос
    logger.info(f"Incoming request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Логируем время выполнения
    process_time = time.time() - start_time
    logger.info(f"Request completed in {process_time:.4f}s with status {response.status_code}")
    
    return response


# Обработчик кастомных исключений
@app.exception_handler(FelendException)
async def felend_exception_handler(request: Request, exc: FelendException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "code": exc.status_code
        }
    )


# Обработчик ошибок валидации SQLAlchemy
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.error(f"Database integrity error: {exc}")
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": "Data integrity violation",
            "code": 400
        }
    )


# Обработчик общих HTTP исключений
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "code": exc.status_code
        }
    )


# Подключение роутеров
app.include_router(auth.router, prefix="/api/v1")
# app.include_router(users.router, prefix="/api/v1")
# app.include_router(surveys.router, prefix="/api/v1")
# app.include_router(google.router, prefix="/api/v1")
# app.include_router(participation.router, prefix="/api/v1")

# Подключаем dev endpoints только в режиме разработки
# if settings.DEBUG:
#     app.include_router(dev.router, prefix="/api/v1")


# Базовые эндпоинты
@app.get("/")
async def root():
    return {
        "message": "Felend API",
        "version": settings.VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check эндпоинт"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )