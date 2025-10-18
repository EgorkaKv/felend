"""
Тесты для Google OAuth аутентификации
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


class TestGoogleOAuth:
    """Базовые тесты для Google OAuth flow"""

    def test_google_login_requires_authentication(self, client: TestClient):
        """Тест, что Google login требует аутентификации"""
        response = client.get("/api/v1/auth/google/login")
        
        # Должен требовать аутентификации  
        assert response.status_code == 401

    def test_google_login_with_auth_returns_url(self, client: TestClient, auth_headers):
        """Тест успешного получения Google OAuth URL"""
        response = client.get("/api/v1/auth/google/login", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Проверяем структуру ответа
        assert "authorization_url" in data
        assert "message" in data
        assert "user_id" in data
        
        # Проверяем, что URL содержит необходимые параметры
        auth_url = data["authorization_url"]
        assert "accounts.google.com/o/oauth2/auth" in auth_url
        assert "client_id=" in auth_url
        assert "redirect_uri=" in auth_url
        assert "scope=" in auth_url
        assert "state=" in auth_url

    def test_google_callback_missing_parameters(self, client: TestClient):
        """Тест Google callback без обязательных параметров"""
        # Без code и state
        response = client.get("/api/v1/auth/google/callback")
        assert response.status_code == 422
        
        # Только с code
        response = client.get("/api/v1/auth/google/callback?code=test_code")
        assert response.status_code == 422
        
        # Только с state
        response = client.get("/api/v1/auth/google/callback?state=test_state")
        assert response.status_code == 422

    def test_google_callback_invalid_state(self, client: TestClient):
        """Тест Google callback с невалидным state"""
        response = client.get("/api/v1/auth/google/callback?code=test_code&state=invalid_state")
        
        # Должен вернуть ошибку из-за невалидного state
        assert response.status_code == 400

    def test_google_callback_malformed_state(self, client: TestClient):
        """Тест Google callback с неправильно сформированным state"""
        malformed_states = [
            "",
            "not.a.jwt",
            "invalid_jwt_token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        ]
        
        for state in malformed_states:
            response = client.get(f"/api/v1/auth/google/callback?code=test_code&state={state}")
            assert response.status_code == 400


class TestGoogleOAuthSecurity:
    """Тесты безопасности Google OAuth"""

    def test_state_parameter_structure(self, client: TestClient, auth_headers):
        """Тест структуры state параметра"""
        response = client.get("/api/v1/auth/google/login", headers=auth_headers)
        
        assert response.status_code == 200
        auth_url = response.json()["authorization_url"]
        
        # Извлекаем state из URL
        state_param = None
        url_parts = auth_url.split("state=")
        if len(url_parts) > 1:
            state_param = url_parts[1].split("&")[0]
        
        assert state_param is not None
        
        # State должен выглядеть как JWT (3 части разделенные точками)
        jwt_parts = state_param.split('.')
        assert len(jwt_parts) == 3
        
        # Каждая часть должна быть base64
        for part in jwt_parts:
            assert len(part) > 0

    def test_different_users_get_different_states(self, client: TestClient, test_user, second_test_user):
        """Тест, что разные пользователи получают разные state токены"""
        from app.core.security import create_access_token
        
        # Создаем токены для разных пользователей
        token1 = create_access_token(data={"sub": str(test_user.id)})
        token2 = create_access_token(data={"sub": str(second_test_user.id)})
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Получаем OAuth URLs для разных пользователей
        response1 = client.get("/api/v1/auth/google/login", headers=headers1)
        response2 = client.get("/api/v1/auth/google/login", headers=headers2)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        url1 = response1.json()["authorization_url"]
        url2 = response2.json()["authorization_url"]
        
        # State параметры должны быть разными
        state1 = url1.split("state=")[1].split("&")[0]
        state2 = url2.split("state=")[1].split("&")[0]
        
        assert state1 != state2

    @patch('app.services.google_auth_service.GoogleAuthService.exchange_code_for_tokens')
    def test_google_callback_with_service_error(self, mock_exchange, client: TestClient, auth_headers):
        """Тест обработки ошибок от Google API"""
        # Мокаем ошибку от Google сервиса
        mock_exchange.side_effect = Exception("Google API Error")
        
        # Получаем валидный state
        login_response = client.get("/api/v1/auth/google/login", headers=auth_headers)
        auth_url = login_response.json()["authorization_url"]
        state = auth_url.split("state=")[1].split("&")[0]
        
        # Пробуем callback с валидным state но Google API должен вернуть ошибку
        response = client.get(f"/api/v1/auth/google/callback?code=test_code&state={state}")
        
        # Должен вернуть ошибку сервера
        assert response.status_code == 500


class TestGoogleOAuthIntegration:
    """Интеграционные тесты"""

    def test_google_login_flow_structure(self, client: TestClient, auth_headers):
        """Тест структуры Google OAuth flow"""
        # 1. Пользователь запрашивает OAuth URL
        response = client.get("/api/v1/auth/google/login", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # 2. Проверяем что получили все необходимые данные
        assert "authorization_url" in data
        assert "message" in data
        assert "user_id" in data
        
        # 3. Проверяем что URL имеет правильную структуру
        auth_url = data["authorization_url"]
        
        required_params = [
            "response_type=code",
            "client_id=",
            "redirect_uri=",
            "scope=",
            "state=",
            "access_type=offline"
        ]
        
        for param in required_params:
            assert param in auth_url
        
        # 4. Проверяем что scope включает необходимые разрешения
        assert "openid" in auth_url
        assert "userinfo.email" in auth_url
        assert "userinfo.profile" in auth_url
        assert "forms" in auth_url