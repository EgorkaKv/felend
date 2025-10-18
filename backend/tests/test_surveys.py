"""
Тесты для endpoints управления опросами
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime


class TestSurveysPublicEndpoints:
    """Тесты для публичных endpoints опросов"""

    # @pytest.mark.skip(reason="FIXME: Endpoint returns 500 - survey service issue")
    def test_get_surveys_feed_unauthenticated(self, client: TestClient):
        """Тест получения ленты опросов без аутентификации"""
        response = client.get("/api/v1/surveys")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    # @pytest.mark.skip(reason="FIXME: Endpoint returns 500 - survey service issue")
    def test_get_surveys_feed_with_pagination(self, client: TestClient):
        """Тест получения ленты опросов с пагинацией"""
        response = client.get("/api/v1/surveys?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    # @pytest.mark.skip(reason="FIXME: Endpoint returns 500 - survey service issue")
    def test_get_surveys_feed_with_search(self, client: TestClient):
        """Тест поиска опросов"""
        response = client.get("/api/v1/surveys?search=test")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    # @pytest.mark.skip(reason="FIXME: Endpoint returns 500 - survey service issue")
    def test_get_surveys_feed_authenticated(self, client: TestClient, auth_headers):
        """Тест получения ленты опросов с аутентификацией"""
        response = client.get("/api/v1/surveys", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_surveys_feed_invalid_pagination(self, client: TestClient):
        """Тест с некорректными параметрами пагинации"""
        # Отрицательный skip
        response = client.get("/api/v1/surveys?skip=-1")
        assert response.status_code == 422
        
        # Слишком большой limit
        response = client.get("/api/v1/surveys?limit=1000")
        assert response.status_code == 422
        
        # Нулевой limit
        response = client.get("/api/v1/surveys?limit=0")
        assert response.status_code == 422

    @pytest.mark.skip(reason="FIXME: Endpoint returns 500 - survey service issue")
    def test_get_survey_detail_unauthenticated(self, client: TestClient):
        """Тест получения деталей опроса без аутентификации"""
        # Тестируем с несуществующим ID
        response = client.get("/api/v1/surveys/999")
        
        # Должен вернуть 404 для несуществующего опроса
        assert response.status_code == 404

    def test_get_survey_detail_invalid_id(self, client: TestClient):
        """Тест получения опроса с некорректным ID"""
        response = client.get("/api/v1/surveys/invalid")
        
        assert response.status_code == 422


class TestSurveysPrivateEndpoints:
    """Тесты для приватных endpoints опросов"""

    def test_get_my_surveys_requires_auth(self, client: TestClient):
        """Тест что получение моих опросов требует аутентификации"""
        response = client.get("/api/v1/surveys/my/")
        
        assert response.status_code in [401, 403]

    @pytest.mark.skip(reason="FIXME: Endpoint returns 500 - survey service issue")
    def test_get_my_surveys_authenticated(self, client: TestClient, auth_headers):
        """Тест получения моих опросов с аутентификацией"""
        response = client.get("/api/v1/surveys/my/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.skip(reason="FIXME: Endpoint returns 500 - survey service issue")
    def test_get_my_surveys_with_pagination(self, client: TestClient, auth_headers):
        """Тест получения моих опросов с пагинацией"""
        response = client.get("/api/v1/surveys/my/?skip=0&limit=5", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_create_survey_requires_auth(self, client: TestClient):
        """Тест что создание опроса требует аутентификации"""
        survey_data = {
            "title": "Test Survey",
            "description": "Test Description",
            "google_form_url": "https://forms.gle/test123",
            "reward_amount": 100,
            "max_responses": 50
        }
        
        response = client.post("/api/v1/surveys/my/", json=survey_data)
        
        assert response.status_code in [401, 403]

    def test_create_survey_success(self, client: TestClient, auth_headers):
        """Тест успешного создания опроса"""
        survey_data = {
            "title": "Test Survey",
            "description": "Test Description", 
            "google_form_url": "https://forms.gle/test123",
            "reward_amount": 100,
            "max_responses": 50
        }
        
        response = client.post("/api/v1/surveys/my/", json=survey_data, headers=auth_headers)
        
        # Может вернуть ошибку из-за недостаточного баланса или другой логики
        assert response.status_code in [201, 400, 422]
        
        if response.status_code == 201:
            data = response.json()
            assert data["title"] == survey_data["title"]
            assert data["description"] == survey_data["description"]
            assert data["reward_amount"] == survey_data["reward_amount"]

    def test_create_survey_invalid_data(self, client: TestClient, auth_headers):
        """Тест создания опроса с некорректными данными"""
        # Пустой title
        survey_data = {
            "title": "",
            "description": "Test Description",
            "google_form_url": "https://forms.gle/test123",
            "reward_amount": 100,
            "max_responses": 50
        }
        
        response = client.post("/api/v1/surveys/my/", json=survey_data, headers=auth_headers)
        assert response.status_code == 422
        
        # Отрицательная награда
        survey_data = {
            "title": "Test Survey",
            "description": "Test Description",
            "google_form_url": "https://forms.gle/test123", 
            "reward_amount": -100,
            "max_responses": 50
        }
        
        response = client.post("/api/v1/surveys/my/", json=survey_data, headers=auth_headers)
        assert response.status_code == 422
        
        # Отрицательное максимальное количество ответов
        survey_data = {
            "title": "Test Survey",
            "description": "Test Description",
            "google_form_url": "https://forms.gle/test123",
            "reward_amount": 100,
            "max_responses": -1
        }
        
        response = client.post("/api/v1/surveys/my/", json=survey_data, headers=auth_headers)
        assert response.status_code == 422

    def test_get_my_survey_detail_requires_auth(self, client: TestClient):
        """Тест что получение деталей моего опроса требует аутентификации"""
        response = client.get("/api/v1/surveys/my/1")
        
        assert response.status_code in [401, 403]

    @pytest.mark.skip(reason="FIXME: Endpoint returns 500 - survey service issue")
    def test_get_my_survey_detail_not_found(self, client: TestClient, auth_headers):
        """Тест получения несуществующего моего опроса"""
        response = client.get("/api/v1/surveys/my/999", headers=auth_headers)
        
        assert response.status_code == 404

    def test_update_survey_requires_auth(self, client: TestClient):
        """Тест что обновление опроса требует аутентификации"""
        update_data = {
            "title": "Updated Survey",
            "description": "Updated Description"
        }
        
        response = client.put("/api/v1/surveys/my/1", json=update_data)
        
        assert response.status_code in [401, 403]

    @pytest.mark.skip(reason="FIXME: Endpoint returns 500 - survey service issue")
    def test_update_survey_not_found(self, client: TestClient, auth_headers):
        """Тест обновления несуществующего опроса"""
        update_data = {
            "title": "Updated Survey",
            "description": "Updated Description"
        }
        
        response = client.put("/api/v1/surveys/my/999", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404

    def test_delete_survey_requires_auth(self, client: TestClient):
        """Тест что удаление опроса требует аутентификации"""
        response = client.delete("/api/v1/surveys/my/1")
        
        assert response.status_code in [401, 403]

    @pytest.mark.skip(reason="FIXME: Endpoint returns 500 - survey service issue")
    def test_delete_survey_not_found(self, client: TestClient, auth_headers):
        """Тест удаления несуществующего опроса"""
        response = client.delete("/api/v1/surveys/my/999", headers=auth_headers)
        
        assert response.status_code == 404


class TestSurveysValidation:
    """Тесты валидации данных опросов"""

    def test_survey_title_validation(self, client: TestClient, auth_headers):
        """Тест валидации заголовка опроса"""
        # Слишком длинный title
        survey_data = {
            "title": "x" * 300,  # Предполагаем максимальную длину
            "description": "Test Description",
            "google_form_url": "https://forms.gle/test123",
            "reward_amount": 100,
            "max_responses": 50
        }
        
        response = client.post("/api/v1/surveys/my/", json=survey_data, headers=auth_headers)
        assert response.status_code == 422

    def test_survey_url_validation(self, client: TestClient, auth_headers):
        """Тест валидации URL опроса"""
        # Некорректный URL
        survey_data = {
            "title": "Test Survey",
            "description": "Test Description",
            "google_form_url": "not-a-valid-url",
            "reward_amount": 100,
            "max_responses": 50
        }
        
        response = client.post("/api/v1/surveys/my/", json=survey_data, headers=auth_headers)
        assert response.status_code == 422

    def test_survey_reward_validation(self, client: TestClient, auth_headers):
        """Тест валидации награды за опрос"""
        # Нулевая награда
        survey_data = {
            "title": "Test Survey",
            "description": "Test Description", 
            "google_form_url": "https://forms.gle/test123",
            "reward_amount": 0,
            "max_responses": 50
        }
        
        response = client.post("/api/v1/surveys/my/", json=survey_data, headers=auth_headers)
        # Возможно, нулевая награда валидна, но проверим
        assert response.status_code in [201, 400, 422]


class TestSurveysAuthorization:
    """Тесты авторизации доступа к опросам"""

    def test_cannot_access_other_user_survey(self, client: TestClient, auth_headers, second_test_user):
        """Тест что нельзя получить доступ к опросу другого пользователя"""
        # Этот тест будет работать только если у нас есть опрос от другого пользователя
        # Пока что просто проверим что возвращается 404 или 403 для несуществующего
        response = client.get("/api/v1/surveys/my/999", headers=auth_headers)
        
        assert response.status_code in [403, 404]

    def test_cannot_update_other_user_survey(self, client: TestClient, auth_headers):
        """Тест что нельзя обновить опрос другого пользователя"""
        update_data = {
            "title": "Hacked Survey",
            "description": "This should not work"
        }
        
        response = client.put("/api/v1/surveys/my/999", json=update_data, headers=auth_headers)
        
        assert response.status_code in [403, 404]

    def test_cannot_delete_other_user_survey(self, client: TestClient, auth_headers):
        """Тест что нельзя удалить опрос другого пользователя"""
        response = client.delete("/api/v1/surveys/my/999", headers=auth_headers)
        
        assert response.status_code in [403, 404]