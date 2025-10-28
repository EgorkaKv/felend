# BottomNavigation Component

## Назначение
Основная навигация приложения для мобильных устройств. Всегда видна внизу экрана.

## Внешний вид

```
┌─────────────────────────────────────┐
│  [🏠]    [📋]    [➕]    [📊]   [👤]  │
│  Лента  Мои     Создать История Профиль │
│         опросы                   (•3) │
└─────────────────────────────────────┘
```

---

## Элементы навигации

### 1. Главная (Лента)
- **Иконка:** 🏠 или feed icon
- **Label:** "Лента" или "Главная"
- **Путь:** `/`
- **Active когда:** текущий маршрут `/`

### 2. Мои опросы
- **Иконка:** 📋 или folder icon
- **Label:** "Мои опросы"
- **Путь:** `/my-surveys`
- **Active когда:** текущий маршрут `/my-surveys`

### 3. Добавить опрос (центральная, выделенная)
- **Иконка:** ➕ или add icon
- **Label:** "Создать" или просто иконка
- **Путь:** `/add-survey`
- **Стиль:**
  - Может быть крупнее других (FAB style)
  - Или обычный размер но с accent color
- **Active когда:** текущий маршрут `/add-survey`

### 4. История
- **Иконка:** 📊 или history icon
- **Label:** "История"
- **Путь:** `/history`
- **Active когда:** текущий маршрут `/history`

### 5. Профиль
- **Иконка:** 👤 или account icon
- **Label:** "Профиль"
- **Путь:** `/profile`
- **Badge:** Количество непрочитанных уведомлений
- **Active когда:** текущий маршрут `/profile` или вложенные `/profile/*`

---

## Состояния элементов

### Default (Inactive)
- **Иконка:** серая (text.secondary)
- **Label:** серый, мелкий (12px)
- **Opacity:** 0.7

### Active (Selected)
- **Иконка:** primary color
- **Label:** primary color, bold
- **Opacity:** 1.0
- **Анимация:** Легкое увеличение иконки

### With Badge (Профиль с уведомлениями)
- **Badge:** Красный кружок с числом
- **Позиция:** Правый верхний угол иконки
- **Max:** "99+" если больше 99

---

## Props

```typescript
interface BottomNavigationProps {
  // Текущий активный маршрут
  currentPath: string
  
  // Количество уведомлений
  notificationCount?: number
  
  // Обработчик навигации
  onNavigate: (path: string) => void
}
```

---

## Поведение

### Навигация
- При клике на элемент:
  1. Вызывается `onNavigate(path)`
  2. React Router переходит на новый маршрут
  3. Элемент становится active
  4. Анимация перехода (опционально)

### Скрытие/показ
- Всегда видна на всех страницах (кроме онбординга и auth)
- Фиксированная позиция внизу
- z-index высокий (выше контента)

### Анимация переключения
- Плавное изменение цвета иконки (200ms)
- Легкое масштабирование active элемента (scale 1.1)

---

## Стили

### Container
- **Position:** fixed
- **Bottom:** 0
- **Width:** 100%
- **Height:** 56px или 64px
- **Background:** white (с тенью сверху)
- **Box-shadow:** 0 -2px 8px rgba(0,0,0,0.1)
- **z-index:** 1100

### Элемент навигации
- **Width:** 20% (для 5 элементов)
- **Display:** flex column
- **Align:** center
- **Padding:** 8px 0
- **Gap:** 4px между иконкой и label

### Иконка
- **Size:** 24x24px
- **Color:** grey (default), primary (active)

### Label
- **Font size:** 11px или 12px
- **Font weight:** 400 (default), 600 (active)
- **Color:** text.secondary (default), primary (active)

---

## Примеры использования

### Базовая реализация
```jsx
<BottomNavigation
  currentPath={location.pathname}
  notificationCount={unreadCount}
  onNavigate={(path) => navigate(path)}
/>
```

### С React Router
```jsx
const BottomNav = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { data: profile } = useProfile()
  
  return (
    <BottomNavigation
      currentPath={location.pathname}
      notificationCount={profile?.unread_notifications}
      onNavigate={navigate}
    />
  )
}
```

---

## Material-UI

Используем `BottomNavigation` и `BottomNavigationAction` из MUI:

```jsx
import { 
  BottomNavigation, 
  BottomNavigationAction 
} from '@mui/material'

import {
  Home,
  Folder,
  Add,
  History,
  AccountCircle
} from '@mui/icons-material'

const Nav = () => {
  const [value, setValue] = useState(0)
  
  return (
    <BottomNavigation
      value={value}
      onChange={(event, newValue) => {
        setValue(newValue)
        navigate(paths[newValue])
      }}
      showLabels
    >
      <BottomNavigationAction label="Лента" icon={<Home />} />
      <BottomNavigationAction label="Мои опросы" icon={<Folder />} />
      <BottomNavigationAction label="Создать" icon={<Add />} />
      <BottomNavigationAction label="История" icon={<History />} />
      <BottomNavigationAction 
        label="Профиль" 
        icon={
          <Badge badgeContent={notificationCount} color="error">
            <AccountCircle />
          </Badge>
        } 
      />
    </BottomNavigation>
  )
}
```

---

## Badge для уведомлений

```jsx
import { Badge } from '@mui/material'

<BottomNavigationAction
  label="Профиль"
  icon={
    <Badge 
      badgeContent={notificationCount} 
      color="error"
      max={99}
    >
      <AccountCircle />
    </Badge>
  }
/>
```

---

## Адаптация для Desktop

На больших экранах (> 768px):
- **Скрываем** bottom navigation
- **Показываем** sidebar (боковую панель) слева
- Те же пункты меню, но вертикально

---

## Accessibility

- **Role:** navigation
- **Aria-label:** "Основная навигация"
- **Keyboard:** Tab для переключения между элементами, Enter для активации
- **Screen reader:** Анонсирует текущий активный раздел
- **Badge:** aria-label для количества уведомлений

---

## Safe Area (для iOS)

Учитываем safe area для iPhone с notch:

```css
.bottom-navigation {
  padding-bottom: env(safe-area-inset-bottom);
}
```

---

## Примечания
- Bottom Navigation - самый важный элемент навигации на мобильных
- Должна быть всегда доступна (кроме auth screens)
- Макс 5 элементов (оптимально)
- Icons должны быть понятными и узнаваемыми
- Labels помогают новым пользователям
- Badge на профиле привлекает внимание к уведомлениям
- Центральная кнопка "+" может быть выделена (FAB)
