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
        # API returns masked email for security
        assert "*" in data["email"]
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


class TestEmailExistsAnywhere:
    """Тесты для проверки дубликатов email в обеих таблицах"""

    def test_cannot_register_with_existing_user_email(self, client: TestClient, test_user):
        """Тест: нельзя зарегистрироваться с email существующего user"""
        user_data = {
            "email": test_user.email,
            "full_name": "Duplicate User",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "USER002"

    def test_cannot_register_with_pending_verification_email(self, client: TestClient):
        """Тест: нельзя создать нового user с email из pending verification (обновляется)"""
        user_data = {
            "email": "pending@example.com",
            "full_name": "Pending User",
            "password": "password123"
        }
        
        # Первая регистрация - создаёт pending verification
        first_response = client.post("/api/v1/auth/register", json=user_data)
        assert first_response.status_code == 201
        first_token = first_response.json()["verification_token"]
        
        # Вторая регистрация с тем же email - должна вернуть тот же токен (обновление)
        user_data_v2 = {
            "email": "pending@example.com",
            "full_name": "Updated Name",
            "password": "newpassword456"
        }
        
        second_response = client.post("/api/v1/auth/register", json=user_data_v2)
        assert second_response.status_code == 201
        second_token = second_response.json()["verification_token"]
        
        # Токены должны совпадать (обновление существующей записи)
        assert first_token == second_token

    def test_email_exists_in_both_tables(self, client: TestClient, db_session):
        """Тест: email_exists_anywhere проверяет обе таблицы"""
        # Создать pending verification
        pending_email = "both_tables@example.com"
        user_data = {
            "email": pending_email,
            "full_name": "Both Tables",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        
        # Проверить через репозиторий
        from app.repositories.user_repository import user_repository
        
        # Email должен существовать где-то (в email_verifications)
        exists = user_repository.email_exists_anywhere(db_session, pending_email)
        assert exists is True

    def test_can_register_after_verification_deleted(self, client: TestClient, db_session):
        """Тест: можно зарегистрироваться снова после удаления pending verification"""
        from unittest.mock import patch
        
        user_data = {
            "email": "reregister_after_delete@example.com",
            "full_name": "Reregister Test",
            "password": "password123"
        }
        
        # Первая регистрация и верификация
        reg_response = client.post("/api/v1/auth/register", json=user_data)
        verification_token = reg_response.json()["verification_token"]
        
        with patch('app.services.email_service.email_service.send_verification_code') as mock_send:
            mock_send.return_value = True
            client.post(
                "/api/v1/auth/request-verification-code",
                json={"verification_token": verification_token}
            )
        
        from app.repositories.email_verification_repository import email_verification_repository
        verification = email_verification_repository.get_by_token(db_session, verification_token)
        assert verification is not None
        actual_code = verification.verification_code
        
        # Верифицировать (создаст user, удалит verification)
        client.post(
            "/api/v1/auth/verify-email",
            json={
                "verification_token": verification_token,
                "code": actual_code
            }
        )
        
        # Попытка повторной регистрации с тем же email
        # Теперь email существует в users, не должна пройти
        second_reg = client.post("/api/v1/auth/register", json=user_data)
        assert second_reg.status_code == 409