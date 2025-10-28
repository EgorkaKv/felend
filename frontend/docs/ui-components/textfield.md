# TextField Component

## Назначение
Универсальный компонент поля ввода текста с валидацией и различными состояниями.

## Варианты

### Standard
- Базовое поле ввода
- Подчеркивание снизу
- Label плавающий

### Outlined (рекомендуется)
- Рамка вокруг поля
- Более заметный
- Label в рамке

### Filled
- Заливка фона
- Label плавающий

---

## Состояния

### Default
- Пустое поле
- Label в верхней позиции (если filled) или внутри (если пустое)
- Placeholder видим когда поле в фокусе

### Focused
- Фокус на поле (пользователь вводит)
- Border/underline меняет цвет (primary)
- Label поднимается вверх (если был внутри)

### Filled
- Поле содержит текст
- Label вверху
- Можно редактировать

### Error
- Валидация не прошла
- Border красный
- Helper text красным показывает ошибку
- Иконка ошибки справа (опционально)

### Disabled
- Поле недоступно для редактирования
- Opacity снижена
- Cursor: not-allowed

### Success (опционально)
- Валидация прошла успешно
- Зеленый border
- Иконка галочки справа

---

## Props

```typescript
interface TextFieldProps {
  // Label над/в поле
  label?: string
  
  // Placeholder текст
  placeholder?: string
  
  // Тип input
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url'
  
  // Значение
  value: string
  
  // Обработчик изменения
  onChange: (value: string) => void
  
  // Обработчик blur (для валидации)
  onBlur?: () => void
  
  // Ошибка валидации
  error?: boolean
  
  // Текст ошибки (показывается под полем)
  helperText?: string
  
  // Disabled состояние
  disabled?: boolean
  
  // Обязательное поле
  required?: boolean
  
  // Multiline (textarea)
  multiline?: boolean
  
  // Кол-во строк (для multiline)
  rows?: number
  
  // Max длина
  maxLength?: number
  
  // Иконка/элемент слева
  startAdornment?: React.ReactNode
  
  // Иконка/элемент справа
  endAdornment?: React.ReactNode
  
  // Автофокус при монтировании
  autoFocus?: boolean
  
  // Автозаполнение браузера
  autoComplete?: string
  
  // Вариант стиля
  variant?: 'standard' | 'outlined' | 'filled'
  
  // Полная ширина
  fullWidth?: boolean
}
```

---

## Специальные типы

### Password Field
- Type: 'password'
- Иконка глаза справа (toggle показать/скрыть)
- При клике на иконку type меняется на 'text'

```jsx
<TextField
  type={showPassword ? 'text' : 'password'}
  endAdornment={
    <IconButton onClick={() => setShowPassword(!showPassword)}>
      {showPassword ? <VisibilityOff /> : <Visibility />}
    </IconButton>
  }
/>
```

### Email Field
- Type: 'email'
- Автоматическая клавиатура с @ на мобильных
- Валидация формата email

### Number Field
- Type: 'number'
- Числовая клавиатура на мобильных
- Min/max значения
- Step для инкремента

---

## Валидация

### Когда валидировать
- **onBlur** - при потере фокуса (рекомендуется)
- **onChange** - в реальном времени (для сложных полей)
- **onSubmit** - при отправке формы (всегда)

### Отображение ошибок
```jsx
<TextField
  label="Email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  onBlur={validateEmail}
  error={!!emailError}
  helperText={emailError || 'Введите ваш email'}
  required
/>
```

### Типы ошибок (helper text)
- "Это поле обязательно"
- "Неверный формат email"
- "Минимум 8 символов"
- "Пароли не совпадают"
- "Только цифры"

---

## Helper Text

**Использование:**
- Подсказка по заполнению (когда нет ошибки)
- Сообщение об ошибке (когда error=true)
- Счетчик символов (опционально)

```jsx
// Подсказка
<TextField
  helperText="Используйте email, на который зарегистрированы"
/>

// Ошибка
<TextField
  error
  helperText="Email обязателен"
/>

// Счетчик
<TextField
  maxLength={100}
  helperText={`${value.length}/100`}
/>
```

---

## Adornments (иконки)

### Start Adornment
- Иконка/текст слева от input
- Например: иконка поиска, знак валюты

```jsx
<TextField
  startAdornment={<SearchIcon />}
  placeholder="Поиск опросов..."
/>
```

### End Adornment
- Иконка/текст справа от input
- Например: показать/скрыть пароль, очистить поле

```jsx
<TextField
  value={search}
  endAdornment={
    search && (
      <IconButton onClick={() => setSearch('')}>
        <ClearIcon />
      </IconButton>
    )
  }
/>
```

---

## Multiline (Textarea)

```jsx
<TextField
  label="Описание"
  multiline
  rows={4}
  maxLength={500}
  placeholder="Введите описание опроса"
  helperText={`${description.length}/500`}
/>
```

---

## Примеры использования

### Email поле
```jsx
<TextField
  label="Email"
  type="email"
  autoComplete="email"
  required
  fullWidth
  error={!!errors.email}
  helperText={errors.email}
/>
```

### Password поле с toggle
```jsx
<TextField
  label="Пароль"
  type={showPassword ? 'text' : 'password'}
  required
  fullWidth
  error={!!errors.password}
  helperText={errors.password || 'Минимум 8 символов'}
  endAdornment={
    <IconButton onClick={() => setShowPassword(!showPassword)}>
      {showPassword ? <VisibilityOff /> : <Visibility />}
    </IconButton>
  }
/>
```

### Поле поиска
```jsx
<TextField
  placeholder="Поиск опросов..."
  fullWidth
  startAdornment={<SearchIcon />}
  endAdornment={
    searchQuery && (
      <IconButton onClick={clearSearch}>
        <ClearIcon />
      </IconButton>
    )
  }
/>
```

### Number поле
```jsx
<TextField
  label="Возраст"
  type="number"
  inputProps={{ min: 0, max: 120, step: 1 }}
  error={!!errors.age}
  helperText={errors.age}
/>
```

---

## Material-UI

Используем `TextField` из Material-UI:
```jsx
import { TextField } from '@mui/material'
```

---

## Accessibility

- **Label** связан с input (for/id)
- **Required** indicator (*) для обязательных полей
- **Error** анонсируется screen readers (aria-invalid, aria-describedby)
- **Helper text** связан с полем через aria-describedby
- **Autocomplete** для автозаполнения браузера

---

## Валидация на клиенте

### Email
```javascript
const validateEmail = (email) => {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(email)
}
```

### Пароль
```javascript
const validatePassword = (password) => {
  return password.length >= 8
}
```

### Required
```javascript
const validateRequired = (value) => {
  return value.trim().length > 0
}
```

---

## Примечания
- Всегда используем labels (не только placeholders)
- Helper text помогает пользователю понять требования
- Валидация onBlur не раздражает пользователя
- Ошибки показываем четко и понятно
- Для мобильных: правильный type для нужной клавиатуры
- Disabled поля должны иметь понятную причину
