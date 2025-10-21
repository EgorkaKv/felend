"""
Тесты для endpoints аутентификации
"""
import pytest
from fastapi.testclient import TestClient


class TestAuthEndpoints:
    """Тесты для /auth/* endpoints"""

    @pytest.mark.smoke
    def test_register_success(self, client: TestClient):
        """Тест успешной регистрации пользователя"""
        user_data = {
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "newpassword123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "verification_token" in data
        assert "email" in data
        assert "message" in data
        assert data["email"] == "newuser@example.com"
        assert "verify your email" in data["message"].lower()

    def test_register_duplicate_email(self, client: TestClient, test_user):
        """Тест регистрации с уже существующим email"""
        user_data = {
            "email": test_user.email,  # Используем email существующего пользователя
            "full_name": "Another User",
            "password": "anotherpassword123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 409

    def test_register_invalid_email(self, client: TestClient):
        """Тест регистрации с невалидным email"""
        user_data = {
            "email": "invalid-email",
            "full_name": "Test User",
            "password": "testpassword123"
        }
        
        response = client.post("api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.smoke
    def test_login_success(self, client: TestClient, test_user, test_user_data):
        """Тест успешного входа"""
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_wrong_password(self, client: TestClient, test_user, test_user_data):
        """Тест входа с неправильным паролем"""
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        """Тест входа несуществующего пользователя"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "somepassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401

    def test_refresh_token_success(self, client: TestClient, test_user):
        """Тест обновления токена"""
        # Сначала логинимся, чтобы получить refresh_token
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"  # из test_user_data
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # Теперь используем refresh_token
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_token_invalid(self, client: TestClient):
        """Тест обновления с невалидным токеном"""
        refresh_data = {"refresh_token": "invalid_token"}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401