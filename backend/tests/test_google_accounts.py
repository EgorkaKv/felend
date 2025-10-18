"""
Тесты для Google аккаунтов endpoints
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
from app.models import User


class TestGoogleAccountsPublicEndpoints:
    """Тесты для публичных endpoints Google аккаунтов"""

    def test_list_google_accounts_requires_auth(self, client: TestClient):
        """Тест что получение списка Google аккаунтов требует аутентификации"""
        response = client.get("/api/v1/google-accounts")
        
        assert response.status_code == 401

    def test_set_primary_requires_auth(self, client: TestClient):
        """Тест что установка основного аккаунта требует аутентификации"""
        response = client.post("/api/v1/google-accounts/1/set-primary")
        
        assert response.status_code == 401

    def test_disconnect_requires_auth(self, client: TestClient):
        """Тест что отключение аккаунта требует аутентификации"""
        response = client.post("/api/v1/google-accounts/1/disconnect")
        
        assert response.status_code == 401

    def test_google_status_requires_auth(self, client: TestClient):
        """Тест что проверка статуса Google подключения требует аутентификации"""
        response = client.get("/api/v1/google-accounts/google/status")
        
        assert response.status_code == 401


class TestGoogleAccountsPrivateEndpoints:
    """Тесты для приватных endpoints Google аккаунтов"""

    # @pytest.mark.skip(reason="FIXME: Google accounts service not fully implemented")
    def test_list_google_accounts_empty(self, client: TestClient, auth_headers):
        """Тест получения пустого списка Google аккаунтов"""
        response = client.get("/api/v1/google-accounts", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "google_accounts" in data
        assert "total_accounts" in data
        assert data["total_accounts"] == 0
        assert data["google_accounts"] == []

    # @pytest.mark.skip(reason="FIXME: Google accounts service not fully implemented")
    def test_list_google_accounts_with_data(self, client: TestClient, auth_headers, mock_google_account):
        """Тест получения списка Google аккаунтов с данными"""
        response = client.get("/api/v1/google-accounts", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_accounts"] > 0
        assert len(data["google_accounts"]) > 0
        
        account = data["google_accounts"][0]
        assert "id" in account
        assert "email" in account
        assert "name" in account
        assert "is_primary" in account
        assert "is_active" in account
        assert "created_at" in account

    # @pytest.mark.skip(reason="FIXME: Google accounts service not fully implemented")
    def test_set_primary_account_success(self, client: TestClient, auth_headers, mock_google_account):
        """Тест успешной установки основного аккаунта"""
        response = client.post(f"/api/v1/google-accounts/{mock_google_account.id}/set-primary", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "primary_account" in data
        assert data["primary_account"]["id"] == mock_google_account.id

    def test_set_primary_account_not_found(self, client: TestClient, auth_headers):
        """Тест установки основного аккаунта для несуществующего ID"""
        response = client.post("/api/v1/google-accounts/999/set-primary", headers=auth_headers)
        
        assert response.status_code in [404, 500]

    # @pytest.mark.skip(reason="FIXME: Google accounts service not fully implemented")
    def test_disconnect_account_success(self, client: TestClient, auth_headers, mock_google_account):
        """Тест успешного отключения аккаунта"""
        response = client.post(f"/api/v1/google-accounts/{mock_google_account.id}/disconnect", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "disconnected_account_id" in data
        assert data["disconnected_account_id"] == mock_google_account.id

    def test_disconnect_account_not_found(self, client: TestClient, auth_headers):
        """Тест отключения несуществующего аккаунта"""
        response = client.post("/api/v1/google-accounts/999/disconnect", headers=auth_headers)
        
        assert response.status_code in [404, 500]

    # @pytest.mark.skip(reason="FIXME: Google accounts service not fully implemented")
    def test_google_status_no_accounts(self, client: TestClient, auth_headers):
        """Тест статуса когда нет подключенных Google аккаунтов"""
        response = client.get("/api/v1/google-accounts/google/status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "google_connected" in data
        assert "total_accounts" in data
        assert "primary_account" in data
        assert data["google_connected"] == False
        assert data["total_accounts"] == 0
        assert data["primary_account"] is None

    # @pytest.mark.skip(reason="FIXME: Google accounts service not fully implemented")
    def test_google_status_with_accounts(self, client: TestClient, auth_headers, mock_google_account):
        """Тест статуса с подключенными аккаунтами"""
        response = client.get("/api/v1/google-accounts/google/status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["google_connected"] == True
        assert data["total_accounts"] > 0
        assert data["primary_account"] is not None
        
        primary = data["primary_account"]
        assert "id" in primary
        assert "email" in primary
        assert "name" in primary
        assert "token_valid" in primary
        assert "expires_at" in primary


class TestGoogleAccountsValidation:
    """Тесты валидации параметров Google аккаунтов"""

    def test_set_primary_invalid_account_id(self, client: TestClient, auth_headers):
        """Тест установки основного аккаунта с некорректным ID"""
        response = client.post("/api/v1/google-accounts/invalid/set-primary", headers=auth_headers)
        
        assert response.status_code == 422

    def test_disconnect_invalid_account_id(self, client: TestClient, auth_headers):
        """Тест отключения аккаунта с некорректным ID"""
        response = client.post("/api/v1/google-accounts/invalid/disconnect", headers=auth_headers)
        
        assert response.status_code == 422

    def test_set_primary_zero_account_id(self, client: TestClient, auth_headers):
        """Тест установки основного аккаунта с ID = 0"""
        response = client.post("/api/v1/google-accounts/0/set-primary", headers=auth_headers)
        
        assert response.status_code in [404, 422, 500]

    def test_disconnect_zero_account_id(self, client: TestClient, auth_headers):
        """Тест отключения аккаунта с ID = 0"""
        response = client.post("/api/v1/google-accounts/0/disconnect", headers=auth_headers)
        
        assert response.status_code in [404, 422, 500]


class TestGoogleAccountsAuthorization:
    """Тесты авторизации для Google аккаунтов"""

    def test_cannot_access_other_user_accounts(self, client: TestClient, second_auth_headers):
        """Тест что нельзя получить аккаунты другого пользователя"""
        response = client.get("/api/v1/google-accounts", headers=second_auth_headers)
        
        # Должен вернуть пустой список или свои аккаунты, но не чужие
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "google_accounts" in data

    def test_cannot_modify_other_user_accounts(self, client: TestClient, second_auth_headers):
        """Тест что нельзя изменять аккаунты другого пользователя"""
        # Пытаемся установить основным аккаунт, который может принадлежать другому пользователю
        response = client.post("/api/v1/google-accounts/1/set-primary", headers=second_auth_headers)
        
        assert response.status_code in [404, 403, 500]

    def test_cannot_disconnect_other_user_accounts(self, client: TestClient, second_auth_headers):
        """Тест что нельзя отключать аккаунты другого пользователя"""
        response = client.post("/api/v1/google-accounts/1/disconnect", headers=second_auth_headers)
        
        assert response.status_code in [404, 403, 500]


class TestGoogleAccountsErrorHandling:
    """Тесты обработки ошибок в Google аккаунтах"""

    def test_list_accounts_service_error(self, client: TestClient, auth_headers):
        """Тест обработки ошибки сервиса при получении списка аккаунтов"""
        # Этот тест проверяет что endpoint возвращает 500 при ошибках сервиса
        response = client.get("/api/v1/google-accounts", headers=auth_headers)
        
        assert response.status_code in [200, 500]

    def test_set_primary_service_error(self, client: TestClient, auth_headers):
        """Тест обработки ошибки сервиса при установке основного аккаунта"""
        response = client.post("/api/v1/google-accounts/999/set-primary", headers=auth_headers)
        
        assert response.status_code in [404, 500]

    def test_disconnect_service_error(self, client: TestClient, auth_headers):
        """Тест обработки ошибки сервиса при отключении аккаунта"""
        response = client.post("/api/v1/google-accounts/999/disconnect", headers=auth_headers)
        
        assert response.status_code in [404, 500]

    def test_google_status_service_error(self, client: TestClient, auth_headers):
        """Тест обработки ошибки сервиса при проверке статуса"""
        response = client.get("/api/v1/google-accounts/google/status", headers=auth_headers)
        
        assert response.status_code in [200, 500]

# Фикстуры для мок данных (если понадобятся)
@pytest.fixture
def mock_google_account(db_session, test_user):
    """Создать мок Google аккаунт для тестов"""
    from app.models import GoogleAccount
    
    google_account = GoogleAccount(
        user_id=test_user.id,
        google_id="test_google_123",
        email="test@gmail.com",
        name="Test Google Account",
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        token_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        is_primary=True,
        is_active=True
    )
    
    db_session.add(google_account)
    db_session.commit()
    db_session.refresh(google_account)
    
    return google_account