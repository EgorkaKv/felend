"""
Конфигурация для интеграции с Google API
"""

from typing import List
from pydantic_settings import BaseSettings


class GoogleSettings(BaseSettings):
    """Настройки Google API"""
    
    # OAuth 2.0 настройки
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    
    # Области доступа для простой авторизации (без Google Forms)
    GOOGLE_AUTH_SCOPES: List[str] = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]
    
    # Области доступа для Google Forms API (для подключения аккаунта)
    GOOGLE_SCOPES: List[str] = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/forms.body.readonly",
        "https://www.googleapis.com/auth/forms.responses.readonly"
    ]
    
    # API endpoints
    GOOGLE_AUTH_URL: str = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL: str = "https://www.googleapis.com/oauth2/v2/userinfo"
    GOOGLE_FORMS_API_BASE: str = "https://forms.googleapis.com/v1"
    
    class ConfigDict:
        env_file = ".env"
        extra = "ignore"


google_settings = GoogleSettings()