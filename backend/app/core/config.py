from pydantic_settings import BaseSettings
from typing import Optional
from urllib.parse import quote


class Settings(BaseSettings):
    # Database - Connection Type
    DB_CONNECTION_TYPE: str = "public"  # "public" or "unix_socket"
    
    # Database - Legacy (for backward compatibility)
    DATABASE_URL: Optional[str] = None
    
    # Database - Public IP Connection (local development)
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "felend"
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"
    
    # Database - Unix Socket Connection (GCP Cloud SQL)
    DB_INSTANCE_CONNECTION_NAME: Optional[str] = None  # Format: project:region:instance
    DB_SOCKET_DIR: str = "/cloudsql"
    
    # Application
    PROJECT_NAME: str = "Felend API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Security
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
    
    @property
    def get_database_url(self) -> str:
        """
        Build database URL based on connection type.
        
        Returns:
            str: Database connection URL
            
        Connection types:
        - "public": Standard TCP/IP connection (local development)
          postgresql://user:password@host:port/database
          
        - "unix_socket": Unix socket connection (GCP Cloud SQL)
          postgresql+psycopg2://user:password@/database?host=/cloudsql/project:region:instance
        """
        
        # Build URL based on connection type
        if self.DB_CONNECTION_TYPE == "unix_socket":
            # GCP Cloud SQL Unix Socket connection
            if not self.DB_INSTANCE_CONNECTION_NAME:
                raise ValueError(
                    "DB_INSTANCE_CONNECTION_NAME is required for unix_socket connection type. "
                    "Format: project:region:instance"
                )
            
            socket_path = f"{self.DB_SOCKET_DIR}/{self.DB_INSTANCE_CONNECTION_NAME}"
            encoded_password = quote(self.DB_PASSWORD, safe="")
            return (
                f"postgresql+psycopg2://{self.DB_USER}:{encoded_password}"
                f"@/{self.DB_NAME}?host={socket_path}"
            )
        else:
            # Public IP connection (default)
            return (
                f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
    
    class ConfigDict:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Создаем глобальный экземпляр настроек
settings = Settings()