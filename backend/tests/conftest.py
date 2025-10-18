"""
Конфигурация тестов и фикстуры
"""
import pytest
import os
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base
from app.api.deps import get_db
from app.models import User, GoogleAccount, Survey, SurveyResponse, BalanceTransaction
from app.repositories.user_repository import user_repository
from app.repositories.google_account_repository import google_account_repository
from app.core.security import get_password_hash, create_access_token

# Используем SQLite в памяти для тестов
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Создание тестовой сессии БД для каждого теста"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def override_get_db(db_session):
    """Override для dependency injection БД"""
    def _override():
        try:
            yield db_session
        finally:
            pass
    return _override


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient с тестовой БД"""
    app.dependency_overrides[get_db] = override_get_db(db_session)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Данные для создания тестового пользователя"""
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123"
    }


@pytest.fixture
def test_user(db_session, test_user_data):
    """Создание тестового пользователя в БД"""
    user = user_repository.create_user(
        db=db_session,
        email=test_user_data["email"],
        full_name=test_user_data["full_name"],
        password=test_user_data["password"]
    )
    return user


@pytest.fixture
def test_user_token(test_user):
    """JWT токен для тестового пользователя"""
    return create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
def auth_headers(test_user_token):
    """Заголовки авторизации для API запросов"""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def second_test_user(db_session):
    """Второй тестовый пользователь"""
    print("Hashing password...")
    password = "testpassword456"
    print(f"Password: {password}")
    
    user = User(
        email="testuser2@example.com",
        full_name="Test User 2",
        hashed_password=get_password_hash(password),
        respondent_code="RESP_000000002",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_google_account_data():
    """Данные для создания тестового Google аккаунта"""
    return {
        "google_id": "123456789",
        "email": "testgoogle@gmail.com",
        "name": "Test Google User",
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token"
    }


@pytest.fixture
def test_google_account(db_session, test_user, test_google_account_data):
    """Создание тестового Google аккаунта в БД"""
    google_account = google_account_repository.create_google_account(
        db=db_session,
        user_id=test_user.id,
        **test_google_account_data
    )
    return google_account


@pytest.fixture
def test_survey_data():
    """Данные для создания тестового опроса"""
    return {
        "title": "Test Survey",
        "description": "Test survey description",
        "google_form_url": "https://docs.google.com/forms/d/test_form_id/viewform",
        "reward_per_response": 10,
        "responses_needed": 100
    }


@pytest.fixture
def mock_google_forms_service():
    """Mock для Google Forms сервиса"""
    class MockGoogleFormsService:
        def extract_form_id_from_url(self, url: str) -> str:
            if "test_form_id" in url:
                return "test_form_id"
            return "mock_form_id"
        
        def get_form_info(self, form_id: str):
            return {
                "form_id": form_id,
                "title": "Mock Form",
                "description": "Mock form description",
                "questions": [],
                "questions_count": 3,
                "form_url": f"https://docs.google.com/forms/d/{form_id}/viewform",
                "responses_url": f"https://docs.google.com/forms/d/{form_id}/responses"
            }
        
        def get_form_responses(self, form_id: str):
            return {
                "responses": [],
                "total_responses": 0
            }
    
    return MockGoogleFormsService()


# Переменные окружения для тестов
@pytest.fixture(autouse=True)
def setup_test_env():
    """Настройка переменных окружения для тестов"""
    os.environ["TESTING"] = "true"
    os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
    os.environ["GOOGLE_CLIENT_ID"] = "test_google_client_id"
    os.environ["GOOGLE_CLIENT_SECRET"] = "test_google_client_secret"
    os.environ["GOOGLE_REDIRECT_URI"] = "http://localhost:8000/auth/google/callback"
    yield
    # Cleanup если нужно