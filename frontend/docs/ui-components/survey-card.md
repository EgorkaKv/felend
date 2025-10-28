# SurveyCard Component

## Назначение
Карточка опроса в ленте. Отображает информацию об опросе и позволяет перейти к прохождению.

## Внешний вид

### Структура карточки

```
┌─────────────────────────────────────┐
│ 🪙 +15 баллов          [Категория]  │  <- Награда + категория
│                                     │
│ Опрос о питании студентов          │  <- Название
│                                     │
│ ⏱️ 5 мин | 📝 10 вопросов          │  <- Время и кол-во
│                                     │
│ 👤 18-25 лет | 👨 Студенты         │  <- Критерии
│                                     │
│ 👤 Иван Петров                     │  <- Автор
│                                     │
│           [Пройти опрос]           │  <- Кнопка
└─────────────────────────────────────┘
```

---

## Элементы карточки

### 1. Награда (вверху слева, крупно)
- **Иконка:** 🪙 или custom icon
- **Текст:** "+15 баллов"
- **Стиль:** 
  - Font size: 20px (bold)
  - Color: accent/gold
  - Выделяется

### 2. Категория (вверху справа, badge)
- **Текст:** "Образование", "Здоровье", "Образ жизни"
- **Стиль:**
  - Small badge/chip
  - Rounded
  - Colored по категории

### 3. Название опроса
- **Текст:** Название опроса
- **Стиль:**
  - Font size: 16px (medium/semibold)
  - Max 2 строки, ellipsis если длиннее
  - Color: text primary

### 4. Метаинформация (время + вопросы)
- **Иконки + текст:**
  - ⏱️ "~5 мин" или "< 5 мин"
  - 📝 "10 вопросов"
- **Стиль:**
  - Font size: 14px
  - Color: text secondary
  - В одной строке через разделитель "|"

### 5. Критерии (если есть)
- **Иконки + текст:**
  - 👤 "18-25 лет"
  - 👨 "Мужчины" или 👩 "Женщины"
  - 💼 "Студенты"
  - 📍 "Москва"
- **Стиль:**
  - Font size: 13px
  - Color: text secondary
  - Wrap если не помещаются
  - Max 2-3 критерия, остальные "..."

### 6. Автор (если есть место)
- **Аватарка (маленькая) + имя**
- **Стиль:**
  - Font size: 13px
  - Color: text secondary

### 7. Кнопка "Пройти опрос"
- **Варианты:**
  - Primary кнопка если доступен
  - Outlined + disabled если не подходит по критериям
  - Badge "Пройдено" если уже пройден
- **Полная ширина**

---

## Состояния

### 1. Available (Доступен)
- Все элементы видны
- Кнопка "Пройти опрос" active
- Hover: легкое поднятие (elevation)
- Cursor: pointer на всю карточку

### 2. Not Suitable (Не подходит по критериям)
- Карточка чуть прозрачнее (opacity 0.7)
- Кнопка disabled
- Tooltip: "Вы не соответствуете критериям"
- Или badge "Не подходит"

### 3. Completed (Пройден)
- Badge "✓ Пройдено" вместо кнопки
- Или badge сверху карточки
- Opacity 0.6
- Нельзя пройти снова (если лимит 1)

### 4. In Progress (В процессе прохождения)
- Badge "В процессе"
- Кнопка "Продолжить"
- Highlight border (опционально)

---

## Props

```typescript
interface SurveyCardProps {
  // Данные опроса
  survey: {
    id: number
    title: string
    description?: string
    reward: number
    questions_count: number
    estimated_time: number // в минутах
    category?: string
    criteria?: {
      age_min?: number
      age_max?: number
      gender?: string[]
      employment?: string[]
      location?: string
    }
    author?: {
      id: number
      name: string
      avatar_url?: string
    }
    is_suitable: boolean
    is_completed: boolean
    is_in_progress?: boolean
  }
  
  // Обработчик клика на кнопку
  onStartSurvey: (surveyId: number) => void
  
  // Компактный режим (меньше информации)
  compact?: boolean
}
```

---

## Взаимодействия

### Клик по карточке
- Открывает детальную информацию
- Опционально: показывает Bottom Sheet / Modal с полным описанием
- Или сразу переходит к прохождению

### Клик по кнопке "Пройти"
1. Проверка критериев (на клиенте)
2. Если подходит → callback `onStartSurvey(surveyId)`
3. Если не подходит → tooltip / snackbar с объяснением

### Hover (Desktop)
- Легкое поднятие карточки (elevation 2 → 4)
- Transition 200ms
- Cursor pointer

---

## Адаптация

### Mobile
- Вертикальное расположение элементов
- Полная ширина
- Больше padding (16px)
- Кнопка полной ширины

### Desktop
- Может быть в Grid (2-3 колонки)
- Фиксированная высота (или max-height)
- Hover эффекты

---

## Форматирование данных

### Время прохождения
```javascript
const formatTime = (minutes) => {
  if (minutes < 5) return '< 5 мин'
  if (minutes < 60) return `~${minutes} мин`
  const hours = Math.floor(minutes / 60)
  return `~${hours} ч`
}
```

### Критерии
```javascript
const formatCriteria = (criteria) => {
  const items = []
  
  if (criteria.age_min || criteria.age_max) {
    items.push(`${criteria.age_min || 0}-${criteria.age_max || 100} лет`)
  }
  
  if (criteria.gender && criteria.gender.length < 3) {
    items.push(criteria.gender.map(g => genderLabels[g]).join(', '))
  }
  
  if (criteria.employment) {
    items.push(criteria.employment.map(e => employmentLabels[e]).join(', '))
  }
  
  if (criteria.location) {
    items.push(criteria.location)
  }
  
  return items.slice(0, 3) // Макс 3 критерия
}
```

---

## Примеры использования

### Базовая карточка
```jsx
<SurveyCard
  survey={survey}
  onStartSurvey={handleStartSurvey}
/>
```

### Компактная карточка
```jsx
<SurveyCard
  survey={survey}
  onStartSurvey={handleStartSurvey}
  compact
/>
```

---

## Material-UI компоненты

```jsx
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Chip,
  Button,
  Avatar,
  Box
} from '@mui/material'
```

---

## Skeleton (Loading)

При загрузке показываем skeleton:
```jsx
<Card>
  <CardContent>
    <Skeleton variant="text" width="60%" height={30} />
    <Skeleton variant="text" width="80%" />
    <Skeleton variant="text" width="40%" />
    <Skeleton variant="rectangular" height={40} sx={{ mt: 2 }} />
  </CardContent>
</Card>
```

---

## Accessibility

- **Role:** article или listitem (если в списке)
- **Aria-label:** Полное название опроса
- **Keyboard:** Tab для фокуса, Enter для клика
- **Screen reader:** Вся важная информация доступна

---

## Примечания
- Карточка должна быть компактной но информативной
- Награда - самый важный элемент (выделяем)
- Кнопка "Пройти" всегда видна и доступна
- Критерии помогают понять подходит ли опрос
- Hover эффекты улучшают UX на desktop
- Состояние "Пройдено" предотвращает дубли
