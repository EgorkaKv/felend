# Button Component

## Назначение
Универсальный компонент кнопки с различными вариантами стилей и состояниями.

## Варианты (Variants)

### 1. Primary
- **Назначение:** Основное действие на странице
- **Стиль:**
  - Заливка: primary color (например, #2196F3)
  - Текст: белый
  - Border: нет
  - Hover: затемнение на 10%
  - Active: затемнение на 20%
- **Использование:** "Зарегистрироваться", "Войти", "Добавить опрос", "Пройти опрос"

### 2. Outlined
- **Назначение:** Вторичное действие
- **Стиль:**
  - Заливка: transparent
  - Border: 1px primary color
  - Текст: primary color
  - Hover: light primary background (opacity 0.08)
- **Использование:** "Отмена", "Открыть снова", "Приостановить"

### 3. Text
- **Назначение:** Минимальное действие, ссылки
- **Стиль:**
  - Заливка: transparent
  - Border: нет
  - Текст: primary color
  - Hover: light background
- **Использование:** "Пропустить", "Изменить email", "Посмотреть все"

### 4. OAuth (специальный)
- **Назначение:** OAuth кнопки (Google и т.д.)
- **Стиль:**
  - Заливка: белый
  - Border: 1px серый
  - Текст: темно-серый
  - Иконка слева (Google logo)
  - Hover: светло-серый фон
- **Использование:** "Войти через Google"

---

## Состояния

### Default
- Нормальное состояние
- Можно нажать

### Hover
- При наведении мыши
- Изменение цвета фона/границы

### Active / Pressed
- При нажатии
- Более темный цвет

### Disabled
- Недоступна для нажатия
- Opacity: 0.5
- Cursor: not-allowed
- Нет hover эффектов

### Loading
- Показывает spinner/loader
- Disabled
- Текст может быть заменен или скрыт
- Например: "Вход..." с spinner

---

## Props (Свойства)

```typescript
interface ButtonProps {
  // Вариант кнопки
  variant?: 'primary' | 'outlined' | 'text' | 'oauth'
  
  // Размер
  size?: 'small' | 'medium' | 'large'
  
  // Полная ширина
  fullWidth?: boolean
  
  // Disabled состояние
  disabled?: boolean
  
  // Loading состояние
  loading?: boolean
  
  // Текст кнопки
  children: React.ReactNode
  
  // Иконка слева
  startIcon?: React.ReactNode
  
  // Иконка справа
  endIcon?: React.ReactNode
  
  // Обработчик клика
  onClick?: () => void
  
  // Тип кнопки (для форм)
  type?: 'button' | 'submit' | 'reset'
  
  // Дополнительные CSS классы
  className?: string
  
  // Цвет (для особых случаев, например, красная кнопка "Удалить")
  color?: 'primary' | 'error' | 'success'
}
```

---

## Размеры

### Small
- Height: 32px
- Padding: 8px 16px
- Font size: 14px
- **Использование:** Компактные интерфейсы, вторичные действия

### Medium (default)
- Height: 40px
- Padding: 10px 20px
- Font size: 16px
- **Использование:** Большинство кнопок

### Large
- Height: 48px
- Padding: 12px 24px
- Font size: 18px
- **Использование:** Основные CTA, мобильные устройства

---

## Примеры использования

### Базовая primary кнопка
```jsx
<Button variant="primary" onClick={handleSubmit}>
  Войти
</Button>
```

### Кнопка с loading
```jsx
<Button 
  variant="primary" 
  loading={isLoading}
  disabled={isLoading}
>
  {isLoading ? 'Вход...' : 'Войти'}
</Button>
```

### Кнопка с иконкой
```jsx
<Button 
  variant="outlined" 
  startIcon={<AddIcon />}
>
  Добавить опрос
</Button>
```

### OAuth кнопка
```jsx
<Button 
  variant="oauth" 
  fullWidth
  startIcon={<GoogleIcon />}
  onClick={handleGoogleLogin}
>
  Войти через Google
</Button>
```

### Полная ширина
```jsx
<Button 
  variant="primary" 
  fullWidth
  size="large"
>
  Зарегистрироваться
</Button>
```

### Кнопка удаления (error color)
```jsx
<Button 
  variant="outlined" 
  color="error"
  onClick={handleDelete}
>
  Удалить
</Button>
```

---

## Accessibility

- **Role:** button (по умолчанию)
- **Keyboard:** Enter и Space для активации
- **Focus:** Видимый outline при фокусе
- **Aria-disabled:** true когда disabled
- **Aria-busy:** true когда loading

---

## Анимации

- **Hover:** Плавный переход цвета (200ms ease)
- **Active:** Мгновенное изменение
- **Loading:** Rotation spinner (1s linear infinite)
- **Ripple effect:** При клике (Material-UI волна)

---

## Material-UI

Используем компонент `Button` из Material-UI:
```jsx
import { Button } from '@mui/material'
```

Кастомизация через `styled()` или `sx` prop для специфичных стилей.

---

## Примечания
- Primary кнопка должна быть одна на экране (основное действие)
- Кнопки должны быть достаточно большими для тач-устройств (min 44x44px)
- Текст кнопки - глагол действия ("Войти", "Сохранить", "Отправить")
- Loading состояние предотвращает повторные отправки
- Disabled кнопки должны иметь понятную причину (tooltip или контекст)
