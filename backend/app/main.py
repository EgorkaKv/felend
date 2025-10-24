from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
import time
import logging

from app.core.config import settings
from app.core.exceptions import FelendException
from app.core.middleware import error_handling_middleware
from app.core.error_handlers import (
    felend_exception_handler,
    validation_exception_handler,
    integrity_error_handler
)
from app.api.v1 import (
    auth,
    google_auth,
    users,
    surveys,
    participation,
    google_accounts,
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
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Добавляем middleware для обработки ошибок
@app.middleware("http")
async def add_error_handling(request, call_next):
    return await error_handling_middleware(request, call_next)


app.add_exception_handler(FelendException, felend_exception_handler) # type: ignore
app.add_exception_handler(RequestValidationError, validation_exception_handler) # type: ignore
app.add_exception_handler(IntegrityError, integrity_error_handler) # type: ignore


# Подключение роутеров
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(surveys.router, prefix="/api/v1")
app.include_router(google_auth.router, prefix="/api/v1")
app.include_router(google_accounts.router, prefix="/api/v1")
app.include_router(participation.router, prefix="/api/v1")


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
