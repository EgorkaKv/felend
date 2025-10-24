from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/felend"
    
    # Application
    PROJECT_NAME: str = "Felend API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google API    
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    
    # Google Forms API scopes
    GOOGLE_FORMS_SCOPES: str = "https://www.googleapis.com/auth/forms,https://www.googleapis.com/auth/forms.responses.readonly"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 200
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Система баллов
    WELCOME_BONUS_POINTS: int = 10
    MIN_REWARD_PER_RESPONSE: int = 1
    MAX_REWARD_PER_RESPONSE: int = 50
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string into list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    class ConfigDict:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Создаем глобальный экземпляр настроек
settings = Settings()