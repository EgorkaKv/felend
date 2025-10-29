# Categories API

Эндпоинты для работы с категориями опросов.

---

## Получить список категорий

**GET** `/api/v1/categories`

Получить список всех активных категорий опросов. Публичный эндпоинт, не требует авторизации.

### Параметры запроса

Нет параметров.

### Успешный ответ (200 OK)

```json
{
  "categories": [
    {
      "id": 1,
      "name": "Образование",
      "description": "Опросы связанные с образованием и обучением",
      "is_active": true,
      "created_at": "2025-10-29T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Технологии",
      "description": "Опросы о технологиях и IT",
      "is_active": true,
      "created_at": "2025-10-29T10:00:00Z"
    },
    {
      "id": 3,
      "name": "Здоровье",
      "description": null,
      "is_active": true,
      "created_at": "2025-10-29T10:00:00Z"
    }
  ],
  "total": 3
}
```

### Возможные ошибки

**500 Internal Server Error** - Внутренняя ошибка сервера

```json
{
  "error": {
    "message": "Internal server error",
    "code": "INTERNAL_ERROR",
    "type": "InternalException",
    "details": {},
    "timestamp": "2025-10-29T10:00:00Z",
    "path": "/api/v1/categories"
  }
}
```

---

## Использование категорий в опросах

### При создании опроса (POST /api/v1/surveys/my/)

Вы можете указать список ID категорий в поле `category_ids`:

```json
{
  "google_account_id": 1,
  "google_form_url": "https://docs.google.com/forms/...",
  "reward_per_response": 10,
  "responses_needed": 100,
  "max_responses_per_user": 1,
  "category_ids": [1, 2]
}
```

### При обновлении опроса (PUT /api/v1/surveys/my/{survey_id})

Вы можете обновить категории опроса, передав новый список `category_ids`:

```json
{
  "category_ids": [1, 3]
}
```

**Примечание:** Если передать пустой массив `[]`, все категории будут удалены с опроса.

### При получении опросов

Все эндпоинты получения опросов (`GET /api/v1/surveys`, `GET /api/v1/surveys/{id}`, `GET /api/v1/surveys/my/`) теперь включают массив `categories` в ответе:

```json
{
  "id": 123,
  "title": "Опрос о студенческой жизни",
  "description": "Расскажите о вашем опыте обучения",
  "categories": [
    {
      "id": 1,
      "name": "Образование",
      "description": "Опросы связанные с образованием и обучением",
      "is_active": true,
      "created_at": "2025-10-29T10:00:00Z"
    }
  ],
  ...
}
```

---

## Валидация категорий

При создании или обновлении опроса с `category_ids`, система проверяет:

1. Все указанные категории существуют
2. Все указанные категории активны (is_active=true)

Если валидация не пройдена, вернется ошибка:

**400 Bad Request**
```json
{
  "error": {
    "message": "Invalid category IDs: some categories don't exist or are not active",
    "code": "VALIDATION_ERROR",
    "type": "ValidationException",
    "details": {},
    "timestamp": "2025-10-29T10:00:00Z",
    "path": "/api/v1/surveys/my/"
  }
}
```

---

## Бизнес-логика

- Категории используются для группировки опросов по темам
- Опрос может иметь несколько категорий (many-to-many связь)
- Только активные категории (is_active=true) отображаются в API и могут быть присвоены опросам
- Категории являются справочными данными и управляются администраторами системы
- Удаление категории не удаляет связанные опросы
