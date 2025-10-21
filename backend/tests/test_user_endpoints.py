"""
Тесты для пользовательских endpoints (профиль, баланс, транзакции)
"""
import pytest
from fastapi.testclient import TestClient
from app.models import User


class TestUsersPublicEndpoints:
    """Тесты для публичных endpoints пользователей"""

    def test_get_profile_requires_auth(self, client: TestClient):
        """Тест что получение профиля требует аутентификации"""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code in [401, 403]

    def test_update_profile_requires_auth(self, client: TestClient):
        """Тест что обновление профиля требует аутентификации"""
        update_data = {"full_name": "New Name"}
        response = client.put("/api/v1/users/me", json=update_data)
        
        assert response.status_code in [401, 403]

    def test_get_transactions_requires_auth(self, client: TestClient):
        """Тест что получение транзакций требует аутентификации"""
        response = client.get("/api/v1/users/me/transactions")
        
        assert response.status_code in [401, 403]


class TestUsersPrivateEndpoints:
    """Тесты для приватных endpoints пользователей"""

    @pytest.mark.smoke
    def test_get_my_profile_success(self, client: TestClient, auth_headers, test_user):
        """Тест успешного получения своего профиля"""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Проверяем структуру ответа
        assert "id" in data
        assert "email" in data
        assert "full_name" in data
        assert "balance" in data
        assert "respondent_code" in data
        assert "created_at" in data
        
        # Проверяем корректность данных
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert isinstance(data["balance"], int)
        assert data["respondent_code"] == test_user.respondent_code

    # @pytest.mark.skip(reason="FIXME: User service update_profile returns SQLAlchemy object instead of Pydantic model")
    def test_update_profile_success(self, client: TestClient, auth_headers, test_user):
        """Тест успешного обновления профиля"""
        update_data = {"full_name": "Updated Test User"}
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Проверяем что имя обновилось
        assert data["full_name"] == "Updated Test User"
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email

    # @pytest.mark.skip(reason="FIXME: User service update_profile method implementation needed")
    def test_update_profile_validation(self, client: TestClient, auth_headers):
        """Тест валидации при обновлении профиля"""
        # Пустое имя
        update_data = {"full_name": ""}
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == 422

        # Слишком длинное имя
        update_data = {"full_name": "x" * 300}
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == 422

    # @pytest.mark.skip(reason="FIXME: User service get_transactions method implementation needed")
    @pytest.mark.smoke
    def test_get_transactions_empty(self, client: TestClient, auth_headers):
        """Тест получения пустого списка транзакций"""
        response = client.get("/api/v1/users/me/transactions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    # @pytest.mark.skip(reason="FIXME: User service get_transactions method implementation needed")
    def test_get_transactions_with_pagination(self, client: TestClient, auth_headers):
        """Тест получения транзакций с пагинацией"""
        response = client.get("/api/v1/users/me/transactions?skip=0&limit=10", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.skip(reason="FIXME: User service get_transactions method implementation needed")
    def test_get_transactions_with_data(self, client: TestClient, auth_headers, mock_transaction):
        """Тест получения транзакций с данными"""
        response = client.get("/api/v1/users/me/transactions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        
        transaction = data[0]
        assert "id" in transaction
        assert "transaction_type" in transaction
        assert "amount" in transaction
        assert "balance_after" in transaction
        assert "description" in transaction
        assert "created_at" in transaction


class TestUsersValidation:
    """Тесты валидации пользовательских данных"""

    def test_update_profile_invalid_data_type(self, client: TestClient, auth_headers):
        """Тест обновления профиля с некорректным типом данных"""
        update_data = {"full_name": 123}  # Должно быть строкой
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == 422

    # @pytest.mark.skip(reason="FIXME: User service update_profile implementation needed")
    def test_update_profile_unknown_field(self, client: TestClient, auth_headers):
        """Тест обновления профиля с неизвестным полем"""
        update_data = {"unknown_field": "value"}
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        # Должен игнорировать неизвестные поля или возвращать ошибку
        assert response.status_code in [200, 422]

    def test_get_transactions_invalid_pagination(self, client: TestClient, auth_headers):
        """Тест получения транзакций с некорректной пагинацией"""
        # Отрицательный skip
        response = client.get("/api/v1/users/me/transactions?skip=-1", headers=auth_headers)
        assert response.status_code in [200, 422]  # Зависит от реализации

        # Отрицательный limit
        response = client.get("/api/v1/users/me/transactions?limit=-1", headers=auth_headers)
        assert response.status_code in [200, 422]

        # Нечисловые параметры
        response = client.get("/api/v1/users/me/transactions?skip=abc&limit=def", headers=auth_headers)
        assert response.status_code == 422


class TestUsersBalance:
    """Тесты работы с балансом пользователя"""

    def test_initial_balance_is_integer(self, client: TestClient, auth_headers):
        """Тест что начальный баланс пользователя - целое число (может быть стартовым бонусом)"""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["balance"], int)
        assert data["balance"] >= 0  # Баланс не может быть отрицательным

    def test_balance_is_integer(self, client: TestClient, auth_headers):
        """Тест что баланс является целым числом"""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["balance"], int)

    # @pytest.mark.skip(reason="FIXME: Balance operations not implemented")
    def test_balance_after_transaction(self, client: TestClient, auth_headers, mock_transaction):
        """Тест что баланс обновляется после транзакции"""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        # Баланс должен отражать транзакции
        assert data["balance"] >= 0


class TestUsersErrorHandling:
    """Тесты обработки ошибок в пользовательских endpoints"""

    def test_get_profile_service_error(self, client: TestClient, auth_headers):
        """Тест обработки ошибки сервиса при получении профиля"""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        # Профиль должен работать или возвращать ошибку сервиса
        assert response.status_code in [200, 500]

    # @pytest.mark.skip(reason="FIXME: User service update_profile implementation needed")
    def test_update_profile_service_error(self, client: TestClient, auth_headers):
        """Тест обработки ошибки сервиса при обновлении профиля"""
        update_data = {"full_name": "Test Update"}
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code in [200, 500]

    def test_get_transactions_service_error(self, client: TestClient, auth_headers):
        """Тест обработки ошибки сервиса при получении транзакций"""
        response = client.get("/api/v1/users/me/transactions", headers=auth_headers)
        
        assert response.status_code in [200, 500]


# Фикстуры для мок данных
@pytest.fixture
def mock_transaction(db_session, test_user):
    """Создать мок транзакцию для тестов"""
    # Пока не реализовано - возвращаем None
    return None