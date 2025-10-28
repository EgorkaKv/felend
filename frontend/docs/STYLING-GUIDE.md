# 🎨 Руководство по стилизации Felend Frontend

## Оглавление
1. [Архитектура стилей](#архитектура-стилей)
2. [Система MUI (Material-UI)](#система-mui-material-ui)
3. [Правила работы со стилями](#правила-работы-со-стилями)
4. [Адаптивный дизайн](#адаптивный-дизайн)
5. [Примеры использования](#примеры-использования)
6. [Частые ошибки](#частые-ошибки)
7. [Best Practices](#best-practices)

---

## Архитектура стилей

Проект использует **3-уровневую систему стилизации**:

```
┌────────────────────────────────────────────┐
│ 1. ГЛОБАЛЬНЫЕ СТИЛИ (index.css)           │
│    • Минимальные reset стили               │
│    • Safe area для iPhone                  │
│    • Базовые оптимизации                   │
├────────────────────────────────────────────┤
│ 2. ТЕМА MUI (src/theme/index.ts)          │
│    • Цветовая палитра                      │
│    • Типографика                           │
│    • Breakpoints                           │
│    • Настройки компонентов                 │
├────────────────────────────────────────────┤
│ 3. КОМПОНЕНТНЫЕ СТИЛИ (sx prop)           │
│    • Локальные переопределения             │
│    • Адаптивные стили                      │
│    • Состояния hover/focus                 │
└────────────────────────────────────────────┘
```

### 📂 Файлы стилей

| Файл | Назначение | Когда редактировать |
|------|-----------|---------------------|
| `src/index.css` | Глобальные базовые стили | **Никогда** (только критические фиксы) |
| `src/theme/index.ts` | Тема приложения | Когда меняете цвета, шрифты, breakpoints |
| Компоненты (`.tsx`) | Локальные стили | Всегда для стилей конкретного компонента |

---

## Система MUI (Material-UI)

### 🎨 Цветовая палитра

```typescript
// Доступ к цветам темы через sx prop
<Box sx={{ 
  bgcolor: 'primary.main',      // #4D96FF (синий)
  color: 'primary.contrastText'  // #FFFFFF
}}>
```

**Основные цвета:**
- `primary.main` - `#4D96FF` (основной синий)
- `secondary.main` - `#6BCF7F` (зеленый)
- `error.main` - `#FF6B6B` (красный)
- `warning.main` - `#FFA500` (оранжевый)
- `success.main` - `#6BCF7F` (зеленый)
- `background.default` - `#F5F7FA` (фон страницы)
- `background.paper` - `#FFFFFF` (фон карточек)
- `text.primary` - `#1A1A1A` (основной текст)
- `text.secondary` - `#6B7280` (вторичный текст)

### 📏 Spacing System

MUI использует **8px базу**:

```typescript
sx={{ 
  p: 2,    // padding: 16px (2 * 8px)
  mt: 3,   // margin-top: 24px (3 * 8px)
  mb: 1.5, // margin-bottom: 12px (1.5 * 8px)
}}
```

**Shorthand свойства:**
- `m` - margin
- `p` - padding
- `mt`, `mr`, `mb`, `ml` - margin-top/right/bottom/left
- `pt`, `pr`, `pb`, `pl` - padding-top/right/bottom/left
- `mx` - margin-left + margin-right
- `my` - margin-top + margin-bottom
- `px` - padding-left + padding-right
- `py` - padding-top + padding-bottom

### 📱 Breakpoints

```typescript
const breakpoints = {
  xs: 0,      // Mobile (0-600px)
  sm: 600,    // Small tablet (600-900px)
  md: 900,    // Tablet (900-1200px)
  lg: 1200,   // Desktop (1200-1536px)
  xl: 1536,   // Large desktop (1536px+)
}
```

---

## Правила работы со стилями

### ✅ ПРАВИЛЬНО - используйте `sx` prop

```typescript
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

// ✅ Используйте sx для стилей
<Box sx={{ 
  p: 2,
  bgcolor: 'background.paper',
  borderRadius: 2,
  boxShadow: 1,
}}>
  <Typography variant="h6" sx={{ mb: 1 }}>
    Заголовок
  </Typography>
</Box>
```

### ❌ НЕПРАВИЛЬНО - не используйте inline styles

```typescript
// ❌ НЕ используйте style prop (хуже производительность)
<Box style={{ 
  padding: '16px',
  backgroundColor: '#ffffff',
  borderRadius: '8px',
}}>

// ❌ НЕ создавайте отдельные CSS файлы для компонентов
import './MyComponent.css'; // Не делайте так!
```

### 🎯 Когда использовать каждый уровень

| Уровень | Когда использовать | Примеры |
|---------|-------------------|---------|
| **index.css** | Глобальные сбросы, фиксы браузеров | safe-area, font-smoothing |
| **theme/index.ts** | Общие для всего приложения настройки | Цвета, шрифты, размеры |
| **sx prop** | Все остальное | Layout, spacing, colors, responsive |

---

## Адаптивный дизайн

### 📱 Responsive Values

MUI позволяет задавать разные значения для разных breakpoints:

```typescript
// Метод 1: Объект
<Box sx={{
  width: { 
    xs: '100%',    // Mobile: 100%
    sm: '100%',    // Small tablet: 100%
    md: '600px',   // Tablet: 600px
    lg: '800px',   // Desktop: 800px
  },
  p: {
    xs: 2,   // Mobile: 16px
    md: 4,   // Desktop+: 32px
  }
}}>

// Метод 2: Массив (xs, sm, md, lg, xl)
<Typography 
  sx={{ 
    fontSize: ['1rem', '1.1rem', '1.25rem', '1.5rem'] 
  }}
>
```

### 🎯 Mobile-First подход

Всегда начинайте с мобильной версии:

```typescript
// ✅ ПРАВИЛЬНО: Mobile-first
<Box sx={{
  p: 2,              // Базовый padding для mobile
  md: { p: 4 },      // Больше padding на desktop
  bgcolor: 'white',  // Базовый цвет
}}>

// ❌ НЕПРАВИЛЬНО: Desktop-first
<Box sx={{
  p: 4,              // Слишком много на mobile
  xs: { p: 2 },      // Приходится уменьшать
}}>
```

### 📐 Container для ограничения ширины

```typescript
import Container from '@mui/material/Container';

// Автоматически адаптируется к breakpoints
<Container maxWidth="md" sx={{ py: 3 }}>
  {/* Контент ограничен 900px (md) */}
</Container>

// Размеры maxWidth:
// xs: 444px
// sm: 600px
// md: 900px
// lg: 1200px
// xl: 1536px
```

---

## Примеры использования

### 1️⃣ Адаптивная карточка

```typescript
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';

<Card 
  sx={{ 
    // Базовые стили (mobile)
    p: 2,
    mb: 2,
    borderRadius: 2,
    
    // Tablet и больше
    md: { 
      p: 3,
      mb: 3,
    },
    
    // Hover эффект (только desktop)
    '@media (hover: hover)': {
      '&:hover': {
        transform: 'translateY(-4px)',
        boxShadow: 4,
      }
    },
    
    // Transition для плавности
    transition: 'all 0.2s ease-in-out',
  }}
>
  <CardContent>
    {/* Контент */}
  </CardContent>
</Card>
```

### 2️⃣ Адаптивная сетка

```typescript
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';

// Stack на mobile, Grid на desktop
<Box sx={{
  display: { xs: 'flex', md: 'grid' },
  flexDirection: { xs: 'column', md: 'row' },
  gridTemplateColumns: { md: 'repeat(2, 1fr)' },
  gap: 2,
}}>
  <Box>Колонка 1</Box>
  <Box>Колонка 2</Box>
</Box>

// Или используйте Grid компонент
<Grid container spacing={2}>
  <Grid item xs={12} md={6}>
    Колонка 1
  </Grid>
  <Grid item xs={12} md={6}>
    Колонка 2
  </Grid>
</Grid>
```

### 3️⃣ Адаптивная типографика

```typescript
import Typography from '@mui/material/Typography';

<Typography 
  variant="h4"
  sx={{
    // Mobile: меньше размер
    fontSize: { xs: '1.5rem', md: '2rem' },
    fontWeight: 600,
    mb: { xs: 2, md: 3 },
    
    // Ограничение длины строки для читабельности
    maxWidth: '800px',
    
    // Ellipsis для длинного текста
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  }}
>
  Заголовок страницы
</Typography>
```

### 4️⃣ Sticky header на мобильных

```typescript
import AppBar from '@mui/material/AppBar';

<AppBar 
  position="sticky"
  sx={{
    top: 0,
    zIndex: 1100,
    bgcolor: 'background.paper',
    color: 'text.primary',
    boxShadow: 1,
    
    // Safe area для iPhone с вырезом
    pt: 'env(safe-area-inset-top)',
  }}
>
```

### 5️⃣ Bottom Navigation с Safe Area

```typescript
import BottomNavigation from '@mui/material/BottomNavigation';

<BottomNavigation
  sx={{
    position: 'fixed',
    bottom: 0,
    left: 0,
    right: 0,
    
    // Скрыто на desktop
    display: { xs: 'flex', md: 'none' },
    
    // Safe area для iPhone с вырезом
    pb: 'env(safe-area-inset-bottom)',
    
    // Высота с учетом safe area
    minHeight: 'calc(64px + env(safe-area-inset-bottom))',
  }}
>
```

---

## Частые ошибки

### ❌ Ошибка 1: Использование px вместо spacing

```typescript
// ❌ НЕПРАВИЛЬНО
<Box sx={{ padding: '16px', margin: '24px' }}>

// ✅ ПРАВИЛЬНО
<Box sx={{ p: 2, m: 3 }}>
```

### ❌ Ошибка 2: Прямые цвета вместо темы

```typescript
// ❌ НЕПРАВИЛЬНО
<Box sx={{ backgroundColor: '#4D96FF', color: '#ffffff' }}>

// ✅ ПРАВИЛЬНО
<Box sx={{ bgcolor: 'primary.main', color: 'primary.contrastText' }}>
```

### ❌ Ошибка 3: Забываем про safe area на iPhone

```typescript
// ❌ НЕПРАВИЛЬНО (контент спрячется за вырезом)
<Box sx={{ pt: 2 }}>

// ✅ ПРАВИЛЬНО (работает на всех устройствах)
<Box sx={{ pt: 'max(16px, env(safe-area-inset-top))' }}>
```

### ❌ Ошибка 4: Слишком маленькие touch targets

```typescript
// ❌ НЕПРАВИЛЬНО (кнопка слишком маленькая для пальца)
<IconButton sx={{ width: 24, height: 24 }}>

// ✅ ПРАВИЛЬНО (минимум 44x44px для комфортного нажатия)
<IconButton sx={{ minWidth: 44, minHeight: 44 }}>
```

### ❌ Ошибка 5: Фиксированные размеры на мобильных

```typescript
// ❌ НЕПРАВИЛЬНО
<Box sx={{ width: 800, p: 5 }}>

// ✅ ПРАВИЛЬНО
<Box sx={{ 
  width: { xs: '100%', md: 800 },
  p: { xs: 2, md: 5 },
}}>
```

---

## Best Practices

### 1. Используйте константы для повторяющихся стилей

```typescript
// src/constants/styles.ts
export const cardStyles = {
  borderRadius: 2,
  boxShadow: 1,
  transition: 'all 0.2s ease-in-out',
  '&:hover': {
    boxShadow: 3,
  },
};

// В компоненте
<Card sx={{ ...cardStyles, p: 2 }}>
```

### 2. Создавайте переиспользуемые компоненты

```typescript
// src/components/PageContainer.tsx
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';

export const PageContainer = ({ children }) => (
  <Container maxWidth="md">
    <Box sx={{ py: { xs: 2, md: 4 } }}>
      {children}
    </Box>
  </Container>
);

// Использование
<PageContainer>
  <Typography variant="h4">Заголовок</Typography>
  {/* Контент */}
</PageContainer>
```

### 3. Группируйте связанные стили

```typescript
// ✅ ПРАВИЛЬНО: логически сгруппированы
<Box sx={{
  // Layout
  display: 'flex',
  flexDirection: 'column',
  gap: 2,
  
  // Spacing
  p: 2,
  m: 3,
  
  // Visual
  bgcolor: 'white',
  borderRadius: 2,
  boxShadow: 1,
  
  // Responsive
  md: {
    flexDirection: 'row',
    p: 4,
  },
}}>
```

### 4. Оптимизация производительности

```typescript
// Используйте willChange для анимируемых элементов
<Box sx={{
  transition: 'transform 0.2s',
  willChange: 'transform',
  '&:hover': {
    transform: 'translateY(-4px)',
  },
}}>

// Используйте transform вместо top/left для анимаций
// ✅ ПРАВИЛЬНО (GPU-accelerated)
transform: 'translateX(100px)'

// ❌ НЕПРАВИЛЬНО (вызывает reflow)
left: '100px'
```

### 5. Тестирование на разных устройствах

**Chrome DevTools:**
1. F12 → Toggle device toolbar (Ctrl+Shift+M)
2. Тестируйте на: iPhone SE, iPhone 12 Pro, iPad, Desktop

**Проверочный список:**
- [ ] Текст читается на маленьких экранах
- [ ] Кнопки не менее 44x44px
- [ ] Нет горизонтального скролла
- [ ] Контент не прячется за safe area
- [ ] Hover эффекты отключены на touch устройствах
- [ ] Input не зумится на iOS (font-size >= 16px)

---

## 🔧 Отладка проблем

### Проблема: Интерфейс "едет" на мобильных

**Решение:**
1. Проверьте `index.css` - нет ли там `display: flex` на body
2. Убедитесь что используете `Container` вместо фиксированной ширины
3. Проверьте наличие `viewport-fit=cover` в meta viewport

### Проблема: Контент спрятан за bottom navigation

**Решение:**
```typescript
// MainLayout должен иметь padding-bottom
<Box sx={{ 
  pb: { 
    xs: 'calc(64px + env(safe-area-inset-bottom))', 
    md: 0 
  } 
}}>
```

### Проблема: Zoom при фокусе на input (iOS)

**Решение:**
```typescript
// В теме: MuiTextField
'& input': {
  fontSize: '1rem', // Минимум 16px!
}
```

---

## 📚 Полезные ссылки

- [MUI Documentation](https://mui.com/material-ui/getting-started/)
- [MUI System (sx prop)](https://mui.com/system/getting-started/the-sx-prop/)
- [MUI Breakpoints](https://mui.com/material-ui/customization/breakpoints/)
- [CSS Safe Area](https://developer.mozilla.org/en-US/docs/Web/CSS/env())

---

## 🎓 Резюме

**Главные правила:**
1. ✅ Всегда используйте `sx` prop для стилей
2. ✅ Используйте spacing систему (1 = 8px)
3. ✅ Используйте цвета из темы (`primary.main`, `text.secondary`)
4. ✅ Mobile-first подход (базовые стили для xs, переопределение для md+)
5. ✅ Проверяйте safe area на iPhone
6. ✅ Минимум 44x44px для touch элементов
7. ❌ Не используйте inline styles или CSS файлы для компонентов
8. ❌ Не используйте px напрямую (только через spacing)

**Когда редактировать что:**
- `index.css` - **никогда** (только критические фиксы)
- `theme/index.ts` - когда нужны глобальные изменения цветов/шрифтов
- `sx prop` - **всегда** для стилей компонента

