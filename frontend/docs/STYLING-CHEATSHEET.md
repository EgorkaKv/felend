# 🎨 Шпаргалка по стилям Felend

## Быстрый старт

### Базовая структура компонента
```typescript
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';

<Container maxWidth="md" sx={{ py: 3 }}>
  <Box sx={{ 
    p: 2,
    bgcolor: 'background.paper',
    borderRadius: 2,
  }}>
    <Typography variant="h6">Заголовок</Typography>
  </Box>
</Container>
```

---

## Spacing (8px base)

| Значение | Pixels | Когда использовать |
|----------|--------|-------------------|
| `0.5` | 4px | Минимальные отступы |
| `1` | 8px | Маленькие отступы |
| `2` | 16px | **Стандартные отступы** ⭐ |
| `3` | 24px | Средние отступы |
| `4` | 32px | Большие отступы |
| `6` | 48px | Очень большие отступы |
| `8` | 64px | Огромные отступы |

```typescript
sx={{ 
  p: 2,    // padding: 16px
  m: 3,    // margin: 24px
  px: 2,   // padding-left + padding-right: 16px
  py: 3,   // padding-top + padding-bottom: 24px
  mt: 1,   // margin-top: 8px
  mb: 2,   // margin-bottom: 16px
}}
```

---

## Цвета темы

### Основные
```typescript
'primary.main'           // #4D96FF - Синий
'primary.light'          // #7DB3FF
'primary.dark'           // #2174E6
'primary.contrastText'   // #FFFFFF

'secondary.main'         // #6BCF7F - Зеленый
'error.main'             // #FF6B6B - Красный
'warning.main'           // #FFA500 - Оранжевый
'success.main'           // #6BCF7F - Зеленый
```

### Фон и текст
```typescript
'background.default'     // #F5F7FA - Фон страницы
'background.paper'       // #FFFFFF - Фон карточек
'text.primary'           // #1A1A1A - Основной текст
'text.secondary'         // #6B7280 - Вторичный текст
'text.disabled'          // #9CA3AF - Отключенный текст
```

---

## Breakpoints

```typescript
xs: 0       // Mobile (0-600px)
sm: 600     // Small tablet
md: 900     // Tablet
lg: 1200    // Desktop
xl: 1536    // Large desktop
```

### Responsive values
```typescript
// Объект
sx={{ 
  width: { xs: '100%', md: '600px' },
  p: { xs: 2, md: 4 }
}}

// Массив [xs, sm, md, lg, xl]
sx={{ fontSize: ['1rem', '1.1rem', '1.25rem'] }}
```

---

## Частые паттерны

### Карточка
```typescript
<Card sx={{ 
  p: 2,
  borderRadius: 2,
  boxShadow: 1,
  transition: 'all 0.2s',
  '&:hover': { boxShadow: 3 }
}}>
```

### Flex Layout
```typescript
<Box sx={{ 
  display: 'flex',
  flexDirection: { xs: 'column', md: 'row' },
  gap: 2,
  alignItems: 'center',
  justifyContent: 'space-between',
}}>
```

### Grid Layout
```typescript
<Box sx={{ 
  display: 'grid',
  gridTemplateColumns: { 
    xs: '1fr', 
    md: 'repeat(2, 1fr)' 
  },
  gap: 2,
}}>
```

### Центрирование
```typescript
// Вертикально и горизонтально
<Box sx={{ 
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '100vh',
}}>

// Только горизонтально
<Box sx={{ mx: 'auto', maxWidth: 600 }}>
```

### Ограничение текста
```typescript
// Ellipsis на одной строке
<Typography sx={{ 
  overflow: 'hidden',
  textOverflow: 'ellipsis',
  whiteSpace: 'nowrap',
}}>

// Clamp на несколько строк
<Typography sx={{ 
  display: '-webkit-box',
  WebkitLineClamp: 2,
  WebkitBoxOrient: 'vertical',
  overflow: 'hidden',
}}>
```

### Touch-friendly кнопка
```typescript
<Button sx={{ 
  minWidth: 44,
  minHeight: 44,
  p: 2,
}}>
```

---

## Typography Variants

```typescript
<Typography variant="h1">      // 2.5rem, 700
<Typography variant="h2">      // 2rem, 700
<Typography variant="h3">      // 1.75rem, 600
<Typography variant="h4">      // 1.5rem, 600
<Typography variant="h5">      // 1.25rem, 600
<Typography variant="h6">      // 1rem, 600
<Typography variant="body1">   // 1rem (default)
<Typography variant="body2">   // 0.875rem
<Typography variant="button">  // 0.875rem, 600
<Typography variant="caption"> // 0.75rem
```

---

## Safe Area (iPhone)

```typescript
// Top (для Header)
pt: 'env(safe-area-inset-top)'

// Bottom (для Bottom Navigation)
pb: 'env(safe-area-inset-bottom)'

// Комбинация с fallback
pt: 'max(16px, env(safe-area-inset-top))'
pb: 'calc(64px + env(safe-area-inset-bottom))'
```

---

## Shadows

```typescript
boxShadow: 0   // Нет тени
boxShadow: 1   // 0px 2px 4px rgba(0,0,0,0.05)
boxShadow: 2   // 0px 4px 8px rgba(0,0,0,0.08)
boxShadow: 3   // 0px 8px 16px rgba(0,0,0,0.10)
boxShadow: 4   // 0px 12px 24px rgba(0,0,0,0.12)
```

---

## Border Radius

```typescript
borderRadius: 1   // 8px
borderRadius: 2   // 16px (стандарт для карточек)
borderRadius: 3   // 24px
borderRadius: '50%' // Круг
```

---

## Transitions

```typescript
// Базовая
transition: 'all 0.2s'

// С easing
transition: 'all 0.2s ease-in-out'

// Только transform (производительность)
transition: 'transform 0.2s'

// С willChange для оптимизации
sx={{
  willChange: 'transform',
  transition: 'transform 0.2s',
  '&:hover': { transform: 'scale(1.05)' }
}}
```

---

## Pseudo-selectors

```typescript
// Hover (только desktop)
'&:hover': { bgcolor: 'primary.light' }

// Focus
'&:focus': { outline: '2px solid', outlineColor: 'primary.main' }

// Active
'&:active': { transform: 'scale(0.98)' }

// Disabled
'&:disabled': { opacity: 0.5, cursor: 'not-allowed' }

// First/Last child
'&:first-of-type': { mt: 0 }
'&:last-of-type': { mb: 0 }
```

---

## Media Queries

```typescript
// Hover support (отключить на touch)
'@media (hover: hover)': {
  '&:hover': { transform: 'translateY(-4px)' }
}

// Dark mode (если нужно)
'@media (prefers-color-scheme: dark)': {
  bgcolor: '#1a1a1a'
}

// Portrait/Landscape
'@media (orientation: portrait)': {
  flexDirection: 'column'
}
```

---

## Проверочный список Mobile

- [ ] Container с maxWidth
- [ ] Responsive padding: `{ xs: 2, md: 4 }`
- [ ] Touch targets >= 44px
- [ ] Safe area для iPhone
- [ ] font-size >= 16px для input (iOS zoom)
- [ ] Hover только `@media (hover: hover)`
- [ ] Test на iPhone SE, iPhone 12, iPad

---

## Где править стили

| Файл | Когда |
|------|-------|
| `index.css` | ❌ Никогда |
| `theme/index.ts` | Глобальные цвета/шрифты |
| `sx` prop | ✅ Всегда для компонента |

---

## Быстрые команды

### Создать страницу
```typescript
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

export default function MyPage() {
  return (
    <Container maxWidth="md" sx={{ py: 3 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Заголовок
      </Typography>
      <Box sx={{ p: 2, bgcolor: 'white', borderRadius: 2 }}>
        Контент
      </Box>
    </Container>
  );
}
```

### Создать карточку
```typescript
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';

<Card sx={{ borderRadius: 2, boxShadow: 1 }}>
  <CardContent sx={{ p: 2 }}>
    Контент
  </CardContent>
</Card>
```

### Создать форму
```typescript
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';

<Stack spacing={2} component="form">
  <TextField label="Email" fullWidth />
  <TextField label="Password" type="password" fullWidth />
  <Button variant="contained" fullWidth>
    Войти
  </Button>
</Stack>
```

---

## ⚠️ Частые ошибки

| ❌ Неправильно | ✅ Правильно |
|---------------|-------------|
| `padding: '16px'` | `p: 2` |
| `backgroundColor: '#4D96FF'` | `bgcolor: 'primary.main'` |
| `width: 800` | `width: { xs: '100%', md: 800 }` |
| `style={{ ... }}` | `sx={{ ... }}` |
| `className="my-class"` | `sx={{ ... }}` |
| Фиксированные px | Responsive values |

---

📚 **Полная документация:** `docs/STYLING-GUIDE.md`
