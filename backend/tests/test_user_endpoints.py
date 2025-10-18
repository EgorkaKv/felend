import pytest
from fastapi.testclient import TestClient

class TestJWTTokenValidation:
    """Тесты для валидации JWT токенов"""

    def test_me_endpoint_authenticated(self, client: TestClient, auth_headers, test_user):
        """Тест получения информации о текущем пользователе"""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert data["id"] == test_user.id

    def test_protected_endpoint_without_token(self, client: TestClient):
        """Тест доступа к защищенному endpoint без токена"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_protected_endpoint_with_malformed_token(self, client: TestClient):
        """Тест доступа с некорректно сформированным токеном"""
        headers = {"Authorization": "InvalidTokenFormat"}
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 401

    def test_protected_endpoint_with_expired_token(self, client: TestClient):
        """Тест доступа с истекшим токеном"""
        # Используем заведомо истекший токен
        expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwiZXhwIjoxNjAwMDAwMDAwfQ.invalid"
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 401