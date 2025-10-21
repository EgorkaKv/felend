"""
Тесты для email verification flow
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.models import User, EmailVerification
from app.services.email_verification_service import EmailVerificationService
from datetime import datetime, timedelta, timezone


class TestEmailVerificationFlow:
    """Тесты для полного flow верификации email"""

    @pytest.mark.smoke
    def test_register_returns_verification_token(self, client: TestClient):
        """Тест: регистрация возвращает verification_token"""
        user_data = {
            "email": "test_verification@example.com",
            "full_name": "Test User",
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "verification_token" in data
        assert len(data["verification_token"]) == 36  # UUID length
        assert data["email"] == user_data["email"]

    def test_request_verification_code_success(self, client: TestClient, db_session):
        """Тест: успешный запрос кода верификации"""
        # Создать пользователя и верификацию
        user_data = {
            "email": "code_test@example.com",
            "full_name": "Code Test",
            "password": "testpass123"
        }
        reg_response = client.post("/api/v1/auth/register", json=user_data)
        verification_token = reg_response.json()["verification_token"]
        
        # Мокировать отправку email
        with patch('app.services.email_service.email_service.send_verification_code') as mock_send:
            mock_send.return_value = True
            
            response = client.post(
                "/api/v1/auth/request-verification-code",
                json={"verification_token": verification_token}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "email_masked" in data
        assert "@" in data["email_masked"]
        assert "***" in data["email_masked"]

    def test_request_verification_code_invalid_token(self, client: TestClient):
        """Тест: запрос кода с невалидным токеном (валидный UUID, но не существующий)"""
        # Используем валидный UUID формат, который не существует в БД
        import uuid
        fake_uuid = str(uuid.uuid4())
        
        response = client.post(
            "/api/v1/auth/request-verification-code",
            json={"verification_token": fake_uuid}
        )
        
        assert response.status_code == 404
        assert "error" in response.json()

    def test_verify_email_success(self, client: TestClient, db_session):
        """Тест: успешная верификация email"""
        # Регистрация
        user_data = {
            "email": "verify_success@example.com",
            "full_name": "Verify Success",
            "password": "testpass123"
        }
        reg_response = client.post("/api/v1/auth/register", json=user_data)
        verification_token = reg_response.json()["verification_token"]
        
        # Получить код (мокировать отправку)
        with patch('app.services.email_service.email_service.send_verification_code') as mock_send:
            mock_send.return_value = True
            code_response = client.post(
                "/api/v1/auth/request-verification-code",
                json={"verification_token": verification_token}
            )
        
        # Получить код из БД напрямую для теста
        from app.repositories.email_verification_repository import email_verification_repository
        verification = email_verification_repository.get_by_token(db_session, verification_token)
        if not verification:
            pytest.fail("Verification record not found in DB")
        actual_code = verification.verification_code
        
        # Верифицировать email
        verify_response = client.post(
            "/api/v1/auth/verify-email",
            json={
                "verification_token": verification_token,
                "code": actual_code
            }
        )
        
        assert verify_response.status_code == 200
        data = verify_response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["balance"] == 10  # Welcome bonus

    def test_verify_email_wrong_code(self, client: TestClient, db_session):
        """Тест: верификация с неправильным кодом"""
        # Регистрация
        user_data = {
            "email": "verify_wrong@example.com",
            "full_name": "Verify Wrong",
            "password": "testpass123"
        }
        reg_response = client.post("/api/v1/auth/register", json=user_data)
        verification_token = reg_response.json()["verification_token"]
        
        # Получить код
        with patch('app.services.email_service.email_service.send_verification_code') as mock_send:
            mock_send.return_value = True
            client.post(
                "/api/v1/auth/request-verification-code",
                json={"verification_token": verification_token}
            )
        
        # Попытка верификации с неправильным кодом
        verify_response = client.post(
            "/api/v1/auth/verify-email",
            json={
                "verification_token": verification_token,
                "code": "999999"
            }
        )
        
        assert verify_response.status_code == 400
        data = verify_response.json()
        assert "error" in data
        assert data["error"]["code"] == "VERIFY003"

    def test_verify_email_expired_code(self, client: TestClient, db_session):
        """Тест: верификация с истекшим кодом"""
        # Регистрация
        user_data = {
            "email": "verify_expired@example.com",
            "full_name": "Verify Expired",
            "password": "testpass123"
        }
        reg_response = client.post("/api/v1/auth/register", json=user_data)
        verification_token = reg_response.json()["verification_token"]
        
        # Получить код
        with patch('app.services.email_service.email_service.send_verification_code') as mock_send:
            mock_send.return_value = True
            client.post(
                "/api/v1/auth/request-verification-code",
                json={"verification_token": verification_token}
            )
        
        # Искусственно истечь код
        from app.repositories.email_verification_repository import email_verification_repository
        verification = email_verification_repository.get_by_token(db_session, verification_token)
        if not verification:
            pytest.fail("Verification record not found in DB")
        actual_code = verification.verification_code
        verification.code_expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        db_session.commit()
        
        # Попытка верификации
        verify_response = client.post(
            "/api/v1/auth/verify-email",
            json={
                "verification_token": verification_token,
                "code": actual_code
            }
        )
        
        assert verify_response.status_code == 400

    def test_request_code_rate_limiting(self, client: TestClient, db_session):
        """Тест: rate limiting для запроса кодов"""
        # Регистрация
        user_data = {
            "email": "rate_limit@example.com",
            "full_name": "Rate Limit",
            "password": "testpass123"
        }
        reg_response = client.post("/api/v1/auth/register", json=user_data)
        verification_token = reg_response.json()["verification_token"]
        
        # Первый запрос - успешно
        with patch('app.services.email_service.email_service.send_verification_code') as mock_send:
            mock_send.return_value = True
            first_response = client.post(
                "/api/v1/auth/request-verification-code",
                json={"verification_token": verification_token}
            )
        
        assert first_response.status_code == 200
        
        # Второй запрос сразу же - должен быть заблокирован
        with patch('app.services.email_service.email_service.send_verification_code') as mock_send:
            mock_send.return_value = True
            second_response = client.post(
                "/api/v1/auth/request-verification-code",
                json={"verification_token": verification_token}
            )
        
        assert second_response.status_code == 429
        data = second_response.json()
        assert "error" in data
        assert data["error"]["code"] == "VERIFY005"

    def test_verify_email_max_attempts(self, client: TestClient, db_session):
        """Тест: максимум 5 попыток верификации"""
        # Регистрация
        user_data = {
            "email": "max_attempts@example.com",
            "full_name": "Max Attempts",
            "password": "testpass123"
        }
        reg_response = client.post("/api/v1/auth/register", json=user_data)
        verification_token = reg_response.json()["verification_token"]
        
        # Получить код
        with patch('app.services.email_service.email_service.send_verification_code') as mock_send:
            mock_send.return_value = True
            client.post(
                "/api/v1/auth/request-verification-code",
                json={"verification_token": verification_token}
            )
        
        # Сделать 5 неправильных попыток
        for i in range(5):
            response = client.post(
                "/api/v1/auth/verify-email",
                json={
                    "verification_token": verification_token,
                    "code": "000000"
                }
            )
            if i < 3:
                # Первые 3 попытки - неправильный код (400)
                assert response.status_code == 400
            else:
                # 4-я и 5-я попытки - слишком много попыток (429)
                assert response.status_code == 429

    def test_login_fails_before_verification(self, client: TestClient, db_session):
        """Тест: логин невозможен до верификации email"""
        # Регистрация
        user_data = {
            "email": "unverified_login@example.com",
            "full_name": "Unverified User",
            "password": "testpass123"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Попытка логина
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": user_data["email"],
                "password": user_data["password"]
            }
        )
        
        # Должен вернуть ошибку (пользователь неактивен)
        assert login_response.status_code == 403

    @pytest.mark.smoke
    def test_full_verification_flow(self, client: TestClient, db_session):
        """Тест: полный flow верификации от регистрации до логина"""
        # 1. Регистрация
        user_data = {
            "email": "full_flow@example.com",
            "full_name": "Full Flow User",
            "password": "testpass123"
        }
        reg_response = client.post("/api/v1/auth/register", json=user_data)
        assert reg_response.status_code == 201
        verification_token = reg_response.json()["verification_token"]
        
        # 2. Запрос кода верификации
        with patch('app.services.email_service.email_service.send_verification_code') as mock_send:
            mock_send.return_value = True
            code_response = client.post(
                "/api/v1/auth/request-verification-code",
                json={"verification_token": verification_token}
            )
        assert code_response.status_code == 200
        
        # 3. Получить код из БД
        from app.repositories.email_verification_repository import email_verification_repository
        verification = email_verification_repository.get_by_token(db_session, verification_token)
        if not verification:
            pytest.fail("Verification record not found in DB")
        actual_code = verification.verification_code
        
        # 4. Верифицировать email
        verify_response = client.post(
            "/api/v1/auth/verify-email",
            json={
                "verification_token": verification_token,
                "code": actual_code
            }
        )
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert "access_token" in verify_data
        assert verify_data["user"]["balance"] == 10
        
        # 5. Проверить, что пользователь активен
        from app.repositories.user_repository import user_repository
        user = user_repository.get_by_email(db_session, user_data["email"])
        if not user:
            pytest.fail("User not found in DB")
        assert user.is_active is True
        
        # 6. Проверить, что теперь можно залогиниться
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": user_data["email"],
                "password": user_data["password"]
            }
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data


class TestEmailVerificationValidation:
    """Тесты валидации данных для верификации"""

    def test_verification_token_must_be_uuid(self, client: TestClient):
        """Тест: verification_token должен быть UUID"""
        response = client.post(
            "/api/v1/auth/request-verification-code",
            json={"verification_token": "not-a-uuid"}
        )
        
        assert response.status_code == 422  # Validation error

    def test_verification_code_must_be_6_digits(self, client: TestClient, db_session):
        """Тест: verification_code должен быть 6 цифр"""
        # Создать валидный токен
        user_data = {
            "email": "code_validation@example.com",
            "full_name": "Code Val",
            "password": "testpass123"
        }
        reg_response = client.post("/api/v1/auth/register", json=user_data)
        verification_token = reg_response.json()["verification_token"]
        
        # Попытка верификации с невалидным кодом
        invalid_codes = ["123", "12345", "1234567", "abcdef", "12-456"]
        
        for invalid_code in invalid_codes:
            response = client.post(
                "/api/v1/auth/verify-email",
                json={
                    "verification_token": verification_token,
                    "code": invalid_code
                }
            )
            assert response.status_code == 422


class TestEmailVerificationSecurity:
    """Тесты безопасности email verification"""

    def test_email_is_masked_in_response(self, client: TestClient):
        """Тест: email маскируется в ответе"""
        user_data = {
            "email": "security_test@example.com",
            "full_name": "Security Test",
            "password": "testpass123"
        }
        reg_response = client.post("/api/v1/auth/register", json=user_data)
        verification_token = reg_response.json()["verification_token"]
        
        with patch('app.services.email_service.email_service.send_verification_code') as mock_send:
            mock_send.return_value = True
            response = client.post(
                "/api/v1/auth/request-verification-code",
                json={"verification_token": verification_token}
            )
        
        masked_email = response.json()["email_masked"]
        assert "***" in masked_email
        assert masked_email != user_data["email"]

    def test_cannot_reuse_verification(self, client: TestClient, db_session):
        """Тест: нельзя повторно использовать верификацию"""
        # Полная верификация
        user_data = {
            "email": "reuse_test@example.com",
            "full_name": "Reuse Test",
            "password": "testpass123"
        }
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
        if not verification:
            pytest.fail("Verification record not found in DB")
        actual_code = verification.verification_code
        
        # Первая верификация - успешно
        verify_response = client.post(
            "/api/v1/auth/verify-email",
            json={
                "verification_token": verification_token,
                "code": actual_code
            }
        )
        assert verify_response.status_code == 200
        
        # Попытка повторной верификации - должна быть отклонена
        second_verify = client.post(
            "/api/v1/auth/verify-email",
            json={
                "verification_token": verification_token,
                "code": actual_code
            }
        )
        assert second_verify.status_code == 410  # Already used
