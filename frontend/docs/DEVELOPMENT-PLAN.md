# План разработки Felend Frontend

Пошаговый чеклист задач для разработки платформы Felend. Задачи расположены в порядке выполнения.

---

## Фаза 1: Настройка проекта и базовая инфраструктура

### 1.1 Инициализация проекта
- [x] Проверить установку Node.js (v18+) и npm/yarn
- [ ] Проверить текущую структуру Vite проекта
- [x] Установить все необходимые зависимости

### 1.2 Установка основных библиотек
- [x] Material-UI v5 (`@mui/material`, `@emotion/react`, `@emotion/styled`)
- [x] React Router v6 (`react-router-dom`)
- [x] Redux Toolkit (`@reduxjs/toolkit`, `react-redux`)
- [x] SWR (`swr`)
- [x] Axios для HTTP запросов
- [x] React Hook Form для форм
- [x] Yup для валидации
- [x] date-fns для работы с датами

### 1.3 Настройка TypeScript
- [x] Проверить `tsconfig.json` (strict mode)
- [x] Настроить path aliases (`@/components`, `@/pages`, `@/api`, и т.д.)
- [x] Создать базовые типы (`types/index.ts`)

### 1.4 Настройка окружения
- [x] Создать `.env.example` с переменными окружения
- [x] Настроить `.env.local` для локальной разработки
- [x] Добавить `VITE_API_BASE_URL`
- [x] Добавить `VITE_GOOGLE_CLIENT_ID` (если нужен на фронте)

### 1.5 Структура папок
- [x] Создать структуру папок:
  ```
  src/
  ├── api/           # API клиенты и запросы
  ├── components/    # Переиспользуемые компоненты
  ├── pages/         # Страницы приложения
  ├── store/         # Redux store
  ├── hooks/         # Custom hooks
  ├── utils/         # Утилиты
  ├── types/         # TypeScript типы
  ├── theme/         # MUI тема
  └── constants/     # Константы
  ```

---

## Фаза 2: Базовая настройка и конфигурация

### 2.1 Настройка Material-UI темы
- [x] Создать `theme/index.ts`
- [x] Настроить цветовую палитру (primary, secondary, error, success)
- [x] Настроить типографику
- [x] Настроить breakpoints (mobile-first)
- [x] Настроить spacing (8px base)
- [x] Добавить кастомные цвета для карточек опросов

### 2.2 Настройка Redux Store
- [x] Создать `store/index.ts`
- [x] Создать слайсы:
  - [x] `authSlice` (user, tokens, isAuthenticated)
  - [x] `uiSlice` (loading, errors, snackbar)
- [x] Настроить middleware
- [x] Добавить persist для auth (localStorage)

### 2.3 Настройка API клиента
- [x] Создать `api/client.ts` (axios instance)
- [x] Добавить interceptors для:
  - [x] Добавление Authorization header
  - [x] Refresh token logic
  - [x] Обработка ошибок (401, 403, 500)
- [x] Создать базовые API модули:
  - [x] `api/auth.ts`
  - [x] `api/surveys.ts`
  - [x] `api/users.ts`
  - [x] `api/googleAccounts.ts`
  - [x] `api/categories.ts`

### 2.4 Настройка React Router
- [x] Создать `App.tsx` с роутингом
- [x] Создать `ProtectedRoute` компонент
- [x] Создать `PublicRoute` компонент (redirect если авторизован)
- [x] Определить все маршруты согласно `navigation.md`

### 2.5 Создать базовые типы
- [x] `types/user.ts` (User, DemographicData)
- [x] `types/survey.ts` (Survey, SurveyCard, Criteria)
- [x] `types/transaction.ts` (Transaction)
- [x] `types/googleAccount.ts` (GoogleAccount)
- [x] `types/api.ts` (ApiResponse, ApiError, PaginatedResponse)
- [x] `types/auth.ts` (LoginRequest, RegisterRequest, TokenResponse)

---

## Фаза 3: UI компоненты (базовые)

### 3.1 Button компонент
- [x] Создать `components/Button/Button.tsx`
- [x] Variants: primary, outlined, text
- [x] States: default, hover, active, disabled, loading
- [x] Sizes: small, medium, large
- [x] Props interface + TypeScript
- [x] Storybook/примеры (опционально)

### 3.2 TextField компонент
- [x] Создать `components/TextField/TextField.tsx`
- [x] Types: text, email, password, number
- [x] States: default, focus, error, disabled
- [x] Error message support
- [x] Helper text
- [x] Icons (start/end adornment)
- [x] Integration с React Hook Form

### 3.3 Loader компоненты
- [x] Создать `components/Loader/Loader.tsx` (full page loader)
- [x] Создать `components/SkeletonCard/SkeletonCard.tsx` (для карточек опросов)
- [x] Создать `components/Spinner/Spinner.tsx` (inline spinner)

### 3.4 Snackbar/Toast компонент
- [x] Создать `components/Snackbar/Snackbar.tsx`
- [x] Types: success, error, warning, info
- [x] Auto-dismiss с таймером
- [x] Интеграция с Redux (uiSlice)

### 3.5 EmptyState компонент
- [x] Создать `components/EmptyState/EmptyState.tsx`
- [x] Props: icon, title, subtitle, action button
- [x] Variants для разных сценариев

### 3.6 Dialog/Modal компонент
- [x] Создать `components/Dialog/Dialog.tsx`
- [x] Confirmation dialog variant
- [x] Custom content support

---

## Фаза 4: Аутентификация и онбординг

### 4.1 Welcome Screen
- [x] Создать `pages/WelcomeScreen/WelcomeScreen.tsx`
- [x] Добавить 2-3 слайда с объяснением концепции
- [x] Swiper/Carousel для слайдов
- [x] Кнопки "Далее", "Пропустить", "Начать"
- [x] Сохранение в localStorage (показывать только 1 раз)

### 4.2 Register Page
- [x] Создать `pages/Register/Register.tsx`
- [x] Форма: email, password, confirmPassword
- [x] Валидация (Yup schema)
- [x] Кнопка "Зарегистрироваться через Google"
- [x] API integration: `POST /api/v1/auth/register`
- [x] Обработка ошибок (email уже существует, и т.д.)
- [x] Redirect на `/confirm-email` после успеха

### 4.3 Confirm Email Page
- [x] Создать `pages/ConfirmEmail/ConfirmEmail.tsx`
- [x] Создать `components/PinInput/PinInput.tsx` (6 полей)
- [x] Автоматический запрос кода при монтировании
- [x] Auto-focus и auto-submit
- [x] Таймер (60 секунд) для повторной отправки
- [x] API integration: 
  - [x] `POST /api/v1/auth/request-verification-code`
  - [x] `POST /api/v1/auth/verify-email`
- [x] Rate limiting (максимум 5 попыток)
- [x] Автоматический вход после верификации

### 4.4 Login Page
- [x] Создать `pages/Login/Login.tsx`
- [x] Форма: email, password
- [x] Валидация
- [x] Кнопка "Войти через Google"
- [ ] Чекбокс "Запомнить меня" (опционально) - не реализовано
- [x] API integration: `POST /api/v1/auth/login`
- [x] Сохранение токенов в Redux + localStorage
- [x] Redirect на `/` после успеха

### 4.5 Google OAuth Integration
- [x] Кнопка "Войти через Google" → redirect на `GET /api/v1/auth/google/login`
- [ ] Обработка возврата после OAuth (если нужна отдельная страница) - автоматически на бэкенде
- [x] Автоматический вход с токенами

### 4.6 Auth Logic & Hooks
- [x] Создать `hooks/useAuth.ts`
- [x] Функции: login, logout, register, verifyEmail
- [x] Auto refresh token logic
- [x] Создать `utils/auth.ts` для работы с токенами

---

## Фаза 5: Layout и навигация

### 5.1 Main Layout
- [x] Создать `components/Layout/MainLayout.tsx`
- [x] Header для мобильных (лого + баланс)
- [x] Bottom Navigation
- [x] Outlet для страниц (React Router)

### 5.2 Bottom Navigation
- [x] Создать `components/BottomNavigation/BottomNavigation.tsx`
- [x] 5 пунктов: Главная, Мои опросы, Добавить, История, Профиль
- [x] Иконки (MUI Icons)
- [x] Active state (подсветка текущей страницы)
- [x] Badge на профиле (для уведомлений - убрать в MVP)
- [x] Навигация через React Router

### 5.3 Header компонент
- [x] Создать `components/Header/Header.tsx`
- [x] Логотип Felend (слева)
- [x] Баланс баллов (справа)
- [x] Tooltip для баланса
- [x] Responsive (скрывать на desktop если есть sidebar)

### 5.4 Desktop Sidebar (опционально для MVP)
- [ ] Создать `components/Sidebar/Sidebar.tsx` - отложено
- [ ] Те же пункты что и в Bottom Navigation
- [ ] Показывать только на desktop (breakpoint)
- [ ] Можно отложить на потом

---

## Фаза 6: Главная страница (Лента опросов)

### 6.1 SurveyCard компонент
- [x] Создать `components/SurveyCard/SurveyCard.tsx`
- [x] Отображение:
  - [x] Награда (крупно)
  - [x] Название
  - [ ] Описание - не добавлено в дизайн
  - [x] Категория
  - [x] Время прохождения / кол-во вопросов
  - [x] Кнопка "Пройти"
  - [x] Цветовая тема (фон карточки)
- [x] States: 
  - [x] Доступен (кнопка активна)
  - [x] Не подходит по критериям (кнопка неактивна)
  - [x] Уже пройден (badge "Пройдено")
- [x] Клик на кнопку "Пройти" → переход к прохождению

### 6.2 SearchBar компонент
- [x] Создать `components/SearchBar/SearchBar.tsx`
- [x] Input с иконкой поиска
- [x] Debounce 300ms
- [x] Clear button (X)

### 6.3 FilterButton и FilterModal
- [x] Создать `components/FilterButton/FilterButton.tsx`
- [x] Badge с количеством активных фильтров
- [x] Создать `components/FilterModal/FilterModal.tsx` (Bottom Sheet на мобильных)
- [x] Фильтры:
  - [x] Категория (чекбоксы)
  - [x] Награда (слайдер min-max)
  - [x] Время прохождения (чекбоксы: <5мин, 5-10мин, >10мин)
  - [x] Toggle "Только подходящие мне"
- [x] Кнопки "Применить" и "Сбросить"

### 6.4 Home Feed Page
- [x] Создать `pages/HomeFeed/HomeFeed.tsx`
- [x] Header с поиском и фильтрами
- [x] Список карточек (вертикальный скролл)
- [x] API integration: `GET /api/v1/surveys`
- [x] Query params: search, category, min_reward, max_reward, duration, only_suitable
- [x] SWR для кэширования
- [ ] Pull-to-refresh на мобильных - не реализовано
- [ ] Infinite scroll или pagination - не реализовано
- [x] States:
  - [x] Loading (skeleton cards)
  - [x] Loaded (список карточек)
  - [x] Empty state (нет опросов)
  - [x] No results (поиск не дал результатов)
  - [x] Error state

### 6.5 Получение категорий
- [x] API integration: `GET /api/v1/categories`
- [x] Использовать в фильтрах

---

## Фаза 7: Прохождение опроса

### 7.1 Survey Completion Page
- [x] Создать `pages/SurveyCompletion/SurveyCompletion.tsx`
- [x] Экран ожидания:
  - [x] Инструкция: "Заполните опрос в открывшейся вкладке"
  - [x] Кнопка "Открыть опрос снова"
  - [x] Кнопка "Подтвердить прохождение"
- [x] Открытие Google Form в новой вкладке: `window.open(survey.google_form_url, '_blank')`
- [x] API integration:
  - [x] `POST /api/v1/surveys/{id}/participate` (старт прохождения)
  - [x] `POST /api/v1/surveys/{id}/verify` (верификация прохождения)
- [x] Обработка результата верификации:
  - [x] Успех: snackbar, обновление баланса через Redux
  - [x] Email не найден: показать ошибку

### 7.2 Обновление баланса
- [ ] Создать `hooks/useBalance.ts` - не нужен, используется Redux
- [x] Обновление баланса через Redux store
- [x] Revalidate после прохождения опроса

---

## Фаза 8: Создание опроса

### 8.1 Add Survey Page
- [x] Создать `pages/AddSurvey/AddSurvey.tsx`
- [x] Форма с полями:
  - [x] Google аккаунт (dropdown, если есть подключенные)
  - [x] Ссылка на Google Form (text input, валидация URL с regex)
  - [x] Категория (select из API)
  - [x] Цветовая тема (6 цветов с визуальным выбором)
  - [ ] Критерии респондентов - упрощено для MVP
  - [x] Дополнительная награда (number input, опционально)
  - [x] Количество нужных ответов (number input, опционально)
  - [x] Максимум ответов от одного пользователя (number input, default: 1)
- [x] Валидация на клиенте (Yup + React Hook Form)
- [x] API integration: `POST /api/v1/surveys/my/`
- [x] Проверка наличия Google аккаунтов
- [x] Обработка ошибок
- [x] Redirect на `/my-surveys` после успеха

### 8.2 Color Picker компонент
- [x] Встроен в AddSurveyPage (6 цветов)
- [x] Предустановленная палитра
- [ ] Кнопка "Случайный цвет" - не реализовано
- [x] Preview выбранного цвета (визуальные квадраты)

### 8.3 Criteria Form компоненты
- [ ] Создать `components/CriteriaForm/CriteriaForm.tsx` - отложено на post-MVP
- [ ] Age Range Slider
- [ ] Gender Select
- [ ] Employment Select
- [ ] Income Select
- [ ] Marital Status Select
- [ ] Location Input

---

## Фаза 9: Мои опросы

### 9.1 MySurveyCard компонент
- [x] Используется обычный SurveyCard с дополнительными элементами
- [x] Отображение через SurveyCard
- [x] Меню действий (три точки - IconButton):
  - [ ] "Посмотреть результаты" - не реализовано
  - [x] "Приостановить" / "Возобновить"
  - [ ] "Настройки" - не реализовано
  - [x] "Удалить"

### 9.2 My Surveys Page
- [x] Создать `pages/MySurveys/MySurveys.tsx`
- [x] Список своих опросов
- [x] API integration: `GET /api/v1/surveys/my/`
- [x] Фильтры по статусу (Tabs: Активные / Приостановлены / Завершенные)
- [ ] Поиск по названию - не реализовано
- [x] States:
  - [x] Loading (CircularProgress)
  - [x] Loaded (список)
  - [x] Empty state ("У вас еще нет опросов")
- [x] Кнопка "Создать опрос" в header и empty state

### 9.3 Survey Actions
- [x] Приостановка: `POST /api/v1/surveys/my/{id}/pause`
- [x] Возобновление: `POST /api/v1/surveys/my/{id}/resume`
- [x] Удаление: `DELETE /api/v1/surveys/my/{id}` (с window.confirm)
- [ ] Посмотреть результаты - не реализовано

### 9.4 Автоматическая приостановка
- [ ] Логика: когда баланс = 0, показать snackbar - отложено на бэкенд
- [ ] "Ваши опросы приостановлены из-за нехватки баллов"
- [ ] Обновление статусов опросов

---

## Фаза 10: История транзакций

### 10.1 TransactionItem компонент
- [x] Встроен в HistoryPage как ListItem
- [x] Отображение:
  - [x] Иконка (+ зеленая / - красная) в Avatar
  - [x] Описание транзакции
  - [x] Сумма (+X / -X баллов) как Chip
  - [x] Дата и время (формат: date-fns)
  - [ ] Баланс после операции - есть в типах, не отображается

### 10.2 History Page
- [x] Создать `pages/History/History.tsx`
- [x] Список транзакций (обратный хронологический порядок)
- [x] API integration: `GET /api/v1/users/me/transactions`
- [x] Фильтры: ToggleButtonGroup (Все / Заработано / Потрачено)
- [ ] Pagination или infinite scroll - не реализовано
- [x] States:
  - [x] Loading (CircularProgress)
  - [x] Loaded (список)
  - [x] Empty state ("История пуста")

---

## Фаза 11: Профиль

### 11.1 Profile Page
- [x] Создать `pages/Profile/Profile.tsx`
- [x] Объединен с Profile Edit (вкладки: Информация / Google аккаунты)
- [x] Отображение:
  - [ ] Аватарка - не реализовано
  - [x] Имя (full_name)
  - [x] Email (из Redux)
  - [ ] Баланс баллов - в Header
- [x] Секции:
  - [x] Вкладка "Google аккаунты"
  - [ ] Настройки - не нужно
  - [x] Кнопка "Выход"

### 11.2 Profile Edit Page
- [x] Встроен в ProfilePage (вкладка "Информация")
- [x] Форма:
  - [ ] Аватарка - не реализовано
  - [x] Полное имя (full_name)
  - [x] Демографические данные:
    - [x] Возраст (number)
    - [x] Пол (select)
    - [ ] Занятость - упрощено
    - [ ] Доход - упрощено
    - [ ] Семейное положение - упрощено
    - [x] Род занятий (text)
    - [ ] Локация - упрощено
- [x] API integration: `PUT /api/v1/users/me`
- [x] Все поля опциональные
- [x] Кнопка "Сохранить"

### 11.3 Logout functionality
- [x] Кнопка "Выход" в профиле
- [ ] Confirmation dialog - не реализовано
- [x] Очистка Redux state
- [x] Очистка localStorage (токены через redux-persist)
- [x] Redirect на `/login`

---

## Фаза 12: Google аккаунты

### 12.1 GoogleAccountCard компонент
- [x] Встроен в ProfilePage как ListItem
- [x] Отображение:
  - [ ] Аватарка Google - не реализовано
  - [x] Email
  - [ ] Имя - есть в типах, не отображается
  - [ ] Badge "Основной" - упрощено для MVP
- [x] Меню действий:
  - [ ] "Сделать основным" - API готов, UI не реализован
  - [x] "Отключить" (IconButton)

### 12.2 Google Accounts Page
- [x] Встроен в ProfilePage (вкладка "Google аккаунты")
- [x] Информационный баннер (Alert)
- [x] Список подключенных аккаунтов
- [x] API integration: `GET /api/v1/google-accounts`
- [x] States:
  - [ ] Loading - общий для страницы
  - [x] Empty state (Alert "Нет подключенных аккаунтов")
  - [x] Loaded (список ListItem)
- [x] Кнопка "+ Подключить Google аккаунт"

### 12.3 Google OAuth Flow
- [x] Кнопка подключения → Dialog с информацией (OAuth на бэкенде)
- [ ] Обработка возврата - автоматически на бэкенде
- [x] Обновление списка аккаунтов (mutate)
- [x] Snackbar при подключении

### 12.4 Account Actions
- [ ] Смена основного: `PUT /api/v1/google-accounts/{id}/set-primary` - API готов, UI не реализован
- [x] Отключение: `DELETE /api/v1/google-accounts/{id}`
- [x] Confirmation dialog (window.confirm)
- [x] Обработка ошибки через snackbar

---

## Фаза 13: Обработка ошибок и граничные случаи

### 13.1 Error Boundary
- [ ] Создать `components/ErrorBoundary/ErrorBoundary.tsx` - не реализовано
- [ ] Отображение friendly error при краше приложения
- [ ] Логирование ошибок (console или сервис)

### 13.2 Network Error Handling
- [x] Обработка ошибок через API interceptors
- [ ] Snackbar при потере интернета - частично
- [ ] Retry кнопка - не реализовано
- [x] Автоматическое переподключение (SWR revalidate)

### 13.3 401/403 Handling
- [x] Автоматический refresh token в API interceptors
- [x] Redirect на `/login` если refresh не удался
- [x] Обработка через axios interceptors

### 13.4 500 Error Handling
- [x] Обработка через API error responses
- [x] Snackbar с сообщением об ошибке
- [ ] Кнопка "Попробовать снова" - не везде

### 13.5 Form Validation Errors
- [x] Inline error messages под полями (React Hook Form)
- [ ] Focus на первое поле с ошибкой - частично
- [x] Clear errors on change (React Hook Form автоматически)

---

## Фаза 14: Оптимизация и полировка

### 14.1 Performance Optimization
- [ ] Code splitting (React.lazy для страниц) - не реализовано
- [ ] Lazy loading изображений - не нужно пока
- [ ] Виртуализация длинных списков - не реализовано
- [x] Memoization (useMemo где нужно)
- [x] Debounce для поиска (300ms)

### 14.2 Accessibility (A11y)
- [x] ARIA labels для кнопок (частично через MUI)
- [x] Keyboard navigation (MUI по умолчанию)
- [ ] Focus management - базовая
- [ ] Screen reader support - базовая через MUI
- [x] Color contrast (WCAG AA) - через MUI тему

### 14.3 Анимации и переходы
- [ ] Page transitions - не реализовано
- [x] Button hover effects (MUI)
- [x] Loading spinners (CircularProgress, Spinner)
- [ ] Success animations - не реализовано
- [x] Skeleton loaders (SkeletonCard)

### 14.4 PWA (опционально)
- [ ] Service Worker - не реализовано
- [ ] Manifest.json - не реализовано
- [ ] Installable app - отложено

### 14.5 SEO и Meta tags
- [ ] React Helmet - не реализовано
- [ ] Open Graph tags - не реализовано
- [ ] Twitter Card tags - не реализовано
- [x] Favicon (vite.svg по умолчанию)

---

## Фаза 15: Тестирование

### 15.1 Manual Testing
- [ ] Тестирование всех страниц на мобильных (Chrome DevTools) - требуется с бэкендом
- [ ] Тестирование основных флоу:
  - [ ] Регистрация → верификация → вход
  - [ ] Прохождение опроса → начисление баллов
  - [ ] Создание опроса → проверка в ленте
  - [ ] Управление Google аккаунтами
- [ ] Тестирование на реальном устройстве (Android/iOS)
- [ ] Тестирование на desktop (базовая функциональность)

### 15.2 Edge Cases Testing
- [ ] Нехватка баллов при создании опроса
- [ ] Приостановка опроса при балансе = 0
- [ ] Email не найден при верификации прохождения
- [ ] Отключение последнего Google аккаунта с активными опросами
- [ ] Длинные тексты (overflow, ellipsis)
- [x] Пустые состояния (EmptyState везде)
- [ ] Медленное интернет-соединение

### 15.3 Cross-browser Testing
- [ ] Chrome (основной) - требуется после интеграции
- [ ] Firefox
- [ ] Safari (iOS)
- [ ] Edge

### 15.4 Unit Tests (опционально для MVP)
- [ ] Тесты для утилит - отложено
- [ ] Тесты для Redux slices - отложено
- [ ] Тесты для кастомных хуков - отложено

---

## Фаза 16: Deployment Preparation

### 16.1 Production Build
- [x] `npm run build` без ошибок (747KB / 242KB gzipped)
- [ ] Проверка размера бандла (lighthouse) - требуется оптимизация
- [x] Tree shaking и минификация (Vite автоматически)

### 16.2 Environment Variables
- [x] Настройка `.env.example`
- [x] `.env` для разработки
- [ ] Production `.env` - требуется при деплое
- [x] Проверка API endpoints

### 16.3 Документация для деплоя
- [x] README.md с базовыми инструкциями
- [x] Описание environment variables в `.env.example`
- [x] Build commands (package.json scripts)

---

## Дополнительные задачи (post-MVP)

### Фичи для будущих версий:
- [ ] Уведомления (push и in-app)
- [ ] Forgot Password flow
- [ ] Настройки аккаунта
- [ ] Темная тема
- [ ] Мультиязычность (i18n)
- [ ] Детальная страница опроса
- [ ] Статистика для авторов опросов
- [ ] Рейтинговая система
- [ ] Социальные функции (комментарии, лайки)
- [ ] Продвинутый desktop дизайн

---

## Чеклист завершения MVP

### Обязательные страницы:
- [x] Welcome Screen
- [x] Register
- [x] Login
- [x] Confirm Email
- [x] Home Feed (Лента опросов)
- [x] Survey Completion
- [x] Add Survey
- [x] My Surveys
- [x] History
- [x] Profile
- [x] Profile Edit
- [x] Google Accounts

### Обязательные компоненты:
- [x] Button
- [x] TextField
- [x] SurveyCard
- [x] MySurveyCard
- [x] BottomNavigation
- [x] Header
- [x] Loader/Skeleton
- [x] Snackbar
- [x] EmptyState
- [x] Dialog

### Обязательная функциональность:
- [x] Регистрация и вход
- [x] Email верификация (6-digit код)
- [x] Google OAuth
- [x] Просмотр ленты опросов
- [x] Фильтрация и поиск опросов
- [x] Прохождение опроса
- [x] Верификация прохождения
- [x] Создание опроса
- [x] Управление своими опросами
- [x] История транзакций
- [x] Редактирование профиля
- [x] Управление Google аккаунтами
- [x] Система баллов (начисление/списание)

---

## Приоритеты

### 🔴 Критично (Blocker):
- Авторизация (регистрация, вход, верификация)
- Лента опросов
- Прохождение опроса
- Создание опроса
- Система баллов

### 🟠 Важно (High):
- Мои опросы
- История транзакций
- Профиль и редактирование
- Google аккаунты
- Фильтры и поиск

### 🟡 Желательно (Medium):
- Анимации и переходы
- PWA
- Accessibility улучшения

### 🟢 Опционально (Low):
- Unit тесты
- Storybook
- Продвинутый desktop UI
- Post-MVP фичи

---

**Примечание:** Этот план можно адаптировать в процессе разработки. Некоторые задачи можно делать параллельно или менять порядок в зависимости от приоритетов.
