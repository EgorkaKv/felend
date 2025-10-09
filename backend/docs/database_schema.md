# Схема базы данных Felend

## Обзор архитектуры данных

Felend использует PostgreSQL в качестве основной базы данных и интегрируется с Google Forms API для создания и сбора ответов на опросы. Это позволяет избежать дублирования функционала создания форм и сосредоточиться на системе обмена баллами.

## Основные сущности

### Users (Пользователи)
```sql
users:
- id (PK)
- email (unique)
- hashed_password (nullable для Google auth)
- google_id (unique, nullable)
- full_name
- balance (integer, баллы пользователя)
- is_active
- created_at, updated_at
```

**Особенности:**
- Поддержка двух способов авторизации: email+пароль и Google OAuth
- Баланс баллов хранится как integer для избежания проблем с floating point
- При регистрации пользователь получает приветственный бонус (WELCOME_BONUS_POINTS)

### Surveys (Опросы)
```sql
surveys:
- id (PK)
- title, description
- author_id (FK to users)
- google_form_id (unique) - ID Google формы
- google_form_url - ссылка на форму
- google_responses_url - ссылка на ответы
- questions_count - количество вопросов
- question_types (JSONB) - метаданные о типах вопросов
- reward_per_response - баллов за ответ
- status (enum: draft, active, paused, completed)
- total_responses, responses_needed
- created_at, updated_at
```

**Особенности:**
- Интеграция с Google Forms через google_form_id
- question_types хранит JSON с описанием структуры формы
- Статусы позволяют управлять жизненным циклом опроса
- Система подсчета ответов для автоматического завершения

**Пример question_types:**
```json
{
  "questions": [
    {"type": "text", "required": true, "title": "Ваш возраст"},
    {"type": "choice", "required": true, "options": ["Да", "Нет"], "title": "Согласны ли вы?"},
    {"type": "multiple_choice", "required": false, "options": ["A", "B", "C"], "title": "Выберите все подходящие"}
  ]
}
```

### SurveyResponse (Ответы на опросы)
```sql
survey_responses:
- id (PK)
- survey_id (FK to surveys)
- respondent_id (FK to users)
- google_response_id (unique) - ID ответа в Google Forms
- google_timestamp - время из Google Forms
- is_verified - проверен ли ответ
- reward_paid - выплачена ли награда
- completed_at
```

**Особенности:**
- Связь с Google Forms через google_response_id
- Система верификации ответов перед выплатой баллов
- Предотвращение двойных выплат через reward_paid

### BalanceTransaction (Транзакции баллов)
```sql
balance_transactions:
- id (PK)
- user_id (FK to users)
- transaction_type (enum: earned, spent, bonus)
- amount (integer, может быть отрицательным)
- balance_after - баланс после транзакции
- description
- related_survey_id (FK to surveys, nullable)
- created_at
```

**Особенности:**
- Аудит всех операций с баллами
- balance_after для быстрой проверки консистентности
- Связь с опросом для трекинга источника/назначения баллов

## Enum типы

```python
class TransactionType(enum.Enum):
    EARNED = "earned"     # получил баллы за прохождение
    SPENT = "spent"       # потратил на получение ответов
    BONUS = "bonus"       # приветственный/промо бонус

class SurveyStatus(enum.Enum):
    DRAFT = "draft"           # черновик
    ACTIVE = "active"         # активный
    PAUSED = "paused"         # приостановлен
    COMPLETED = "completed"   # завершен
```

## Индексы и ограничения

- `users.email` - unique index
- `users.google_id` - unique index
- `surveys.google_form_id` - unique index
- `survey_responses.google_response_id` - unique index
- Foreign key constraints для всех связей

## Интеграция с Google Forms API

1. **Создание опроса**: Автор создает форму через Google Forms, система сохраняет metadata
2. **Сбор ответов**: Google Forms собирает ответы, система периодически синхронизирует данные
3. **Верификация**: Проверка валидности ответов перед начислением баллов
4. **Аналитика**: Доступ к ответам через Google Forms API для отображения результатов

## Миграции

Alembic настроен для управления миграциями. Конфигурация поддерживает:
- Автоматическое определение изменений в моделях
- Поддержка PostgreSQL-специфичных типов (JSONB, ENUM)
- Интеграция с переменными окружения