# UI Components - Индекс

Документация всех переиспользуемых UI компонентов Felend.

## Базовые компоненты

- [button.md](./button.md) - Button (кнопки всех типов)
- [textfield.md](./textfield.md) - TextField (поля ввода)

## Навигация

- [bottom-navigation.md](./bottom-navigation.md) - BottomNavigation (нижняя навигация)

## Карточки и списки

- [survey-card.md](./survey-card.md) - SurveyCard (карточка опроса в ленте)

## Будущие компоненты

Компоненты, которые будут добавлены:

### Feedback & Dialogs
- `Snackbar` - уведомления/toasts
- `Dialog` - модальные окна подтверждений
- `BottomSheet` - нижние шторки (мобильные)
- `Alert` / `Banner` - информационные баннеры

### Forms
- `Select` - выпадающие списки
- `Checkbox` - чекбоксы
- `RadioGroup` - радио кнопки
- `Toggle` / `Switch` - переключатели

### Layout
- `Header` - шапка страницы
- `Sidebar` - боковая панель (desktop)
- `Container` - контейнер контента
- `Card` - базовая карточка

### Data Display
- `Avatar` - аватарки
- `Badge` - badges/метки
- `Chip` - chips/теги
- `ProgressBar` - прогресс-бары
- `Skeleton` - skeleton loaders

### Lists
- `MySurveyCard` - карточка своего опроса
- `TransactionItem` - элемент транзакции
- `NotificationItem` - элемент уведомления

### Special
- `BalanceCard` - карточка баланса
- `GoogleAccountCard` - карточка Google аккаунта
- `EmptyState` - пустые состояния
- `ErrorState` - состояния ошибок

---

## Структура документа компонента

Каждый документ компонента содержит:

1. **Назначение** - для чего компонент
2. **Варианты** - разные стили (variants)
3. **Состояния** - все UI состояния
4. **Props** - TypeScript интерфейс свойств
5. **Примеры использования** - код примеры
6. **Material-UI** - какие MUI компоненты используем
7. **Accessibility** - доступность
8. **Примечания** - дополнительная информация

---

## Принципы дизайна

### Мобильная оптимизация
- Компоненты разработаны mobile-first
- Минимальный размер touch target: 44x44px
- Большие кнопки и отступы на мобильных

### Консистентность
- Единый стиль во всем приложении
- Переиспользуемые компоненты
- Material Design guidelines

### Accessibility
- Keyboard navigation
- Screen reader support
- ARIA attributes
- High contrast support

### Performance
- Lazy loading где возможно
- Оптимизированные ре-рендеры
- Виртуализация длинных списков

---

## Material-UI

Основная UI библиотека: **Material-UI (MUI) v5**

```bash
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material
```

### Базовые импорты
```javascript
import { 
  Button, 
  TextField, 
  Card,
  // ... 
} from '@mui/material'

import { 
  Home, 
  Add, 
  // ... 
} from '@mui/icons-material'
```

### Кастомизация темы
```javascript
import { createTheme, ThemeProvider } from '@mui/material/styles'

const theme = createTheme({
  palette: {
    primary: {
      main: '#2196F3',
    },
    // ...
  },
  typography: {
    fontFamily: 'Inter, sans-serif',
    // ...
  },
})
```

---

## Цветовая палитра

### Primary
- Main: `#2196F3` (синий)
- Light: `#64B5F6`
- Dark: `#1976D2`

### Secondary
- Main: `#FF9800` (оранжевый)
- Light: `#FFB74D`
- Dark: `#F57C00`

### Success
- Main: `#4CAF50` (зеленый)

### Error
- Main: `#F44336` (красный)

### Grey
- 50, 100, 200, ... 900

### Text
- Primary: `rgba(0, 0, 0, 0.87)`
- Secondary: `rgba(0, 0, 0, 0.6)`
- Disabled: `rgba(0, 0, 0, 0.38)`

---

## Типографика

### Font Family
- Primary: `'Inter', 'Roboto', sans-serif`

### Sizes
- h1: 32px
- h2: 28px
- h3: 24px
- h4: 20px
- h5: 18px
- h6: 16px
- body1: 16px
- body2: 14px
- caption: 12px

---

## Breakpoints

```javascript
// Material-UI breakpoints
xs: 0px      // extra-small (мобильные)
sm: 600px    // small (большие мобильные, планшеты)
md: 960px    // medium (планшеты, маленькие ноутбуки)
lg: 1280px   // large (десктопы)
xl: 1920px   // extra-large (большие экраны)
```

---

## Spacing

Material-UI spacing (8px base):
- `spacing(1)` = 8px
- `spacing(2)` = 16px
- `spacing(3)` = 24px
- `spacing(4)` = 32px
- etc.

---

## Примечания

- Все компоненты должны быть адаптивными
- Используем Material-UI где возможно
- Кастомизируем через styled() или sx prop
- Следуем Material Design principles
- Accessibility - обязательное требование
