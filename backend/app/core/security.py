from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings
import secrets
import string


# Контекст для хеширования паролей
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=12
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    print('Hashing password...')
    print(f'Password: {password}')
    """Хеширование пароля"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание JWT access токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Создание JWT refresh токена"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """Проверка и декодирование JWT токена"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None


def generate_respondent_code(user_id: int) -> str:
    """Генерация уникального кода респондента"""
    return f"RESP_{user_id:09d}"


def generate_random_string(length: int = 32) -> str:
    """Генерация случайной строки"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def create_oauth_state(user_id: int, frontend_redirect_uri: Optional[str] = None, csrf_token: Optional[str] = None) -> str:
    """
    Создание JWT state для OAuth (подключение Google аккаунта к существующему user)
    
    Используется для flow подключения Google Forms к уже авторизованному пользователю.
    
    Args:
        user_id: ID пользователя
        frontend_redirect_uri: URL фронтенда для редиректа после обработки callback (опционально)
        csrf_token: CSRF токен (генерируется автоматически если не передан)
    
    Returns:
        str: Закодированный JWT state
    """
    if not csrf_token:
        csrf_token = generate_random_string(32)
    
    data = {
        "user_id": user_id,
        "csrf_token": csrf_token,
        "created_at": datetime.now(timezone.utc).timestamp()
    }
    
    # Добавляем frontend_redirect_uri если передан
    if frontend_redirect_uri:
        data["frontend_redirect_uri"] = frontend_redirect_uri
    
    # Время жизни state = 15 минут
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    data.update({"exp": expire, "type": "oauth_state"})
    
    encoded_state = jwt.encode(data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_state


def create_google_auth_state(frontend_redirect_uri: str, csrf_token: Optional[str] = None) -> str:
    """
    Создание JWT state для Google авторизации/регистрации (публичный flow)
    
    Используется для flow регистрации/входа через Google без pre-existing аккаунта.
    
    Args:
        frontend_redirect_uri: URL фронтенда для редиректа после успешной авторизации
        csrf_token: CSRF токен (генерируется автоматически если не передан)
    
    Returns:
        str: Закодированный JWT state
    """
    if not csrf_token:
        csrf_token = generate_random_string(32)
    
    data = {
        "frontend_redirect_uri": frontend_redirect_uri,
        "csrf_token": csrf_token,
        "created_at": datetime.now(timezone.utc).timestamp()
    }
    
    # Время жизни state = 15 минут
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    data.update({"exp": expire, "type": "google_auth_state"})
    
    encoded_state = jwt.encode(data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_state


def verify_oauth_state(state: str) -> Optional[dict]:
    """
    Проверка и декодирование JWT state для OAuth (подключение аккаунта)
    
    Возвращает payload с user_id для flow подключения Google Forms.
    """
    try:
        payload = jwt.decode(state, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "oauth_state":
            return None
        
        # Проверяем что state не истек (это уже делает jwt.decode, но для ясности)
        if datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc) < datetime.now(timezone.utc):
            return None
            
        return payload
    except JWTError:
        return None


def verify_google_auth_state(state: str) -> Optional[dict]:
    """
    Проверка и декодирование JWT state для Google авторизации/регистрации
    
    Возвращает payload с frontend_redirect_uri для публичного auth flow.
    """
    try:
        payload = jwt.decode(state, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "google_auth_state":
            return None
        
        # Проверяем что state не истек
        if datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc) < datetime.now(timezone.utc):
            return None
            
        return payload
    except JWTError:
        return None