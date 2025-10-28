import { createTheme } from '@mui/material/styles';

// Цветовая палитра для карточек опросов
export const surveyCardColors = {
  red: '#FF6B6B',
  orange: '#FFA500',
  yellow: '#FFD93D',
  green: '#6BCF7F',
  blue: '#4D96FF',
  purple: '#9B59B6',
  brown: '#A0826D',
  gray: '#95A5A6',
};

// Создание темы Material-UI
const theme = createTheme({
  // Цветовая схема
  palette: {
    primary: {
      main: '#4D96FF', // Синий
      light: '#7DB3FF',
      dark: '#2174E6',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#6BCF7F', // Зеленый
      light: '#8FDB9F',
      dark: '#4AAF5C',
      contrastText: '#FFFFFF',
    },
    error: {
      main: '#FF6B6B',
      light: '#FF8F8F',
      dark: '#E64545',
    },
    warning: {
      main: '#FFA500',
      light: '#FFB733',
      dark: '#CC8400',
    },
    info: {
      main: '#4D96FF',
    },
    success: {
      main: '#6BCF7F',
    },
    background: {
      default: '#F5F7FA',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#1A1A1A',
      secondary: '#6B7280',
      disabled: '#9CA3AF',
    },
  },

  // Типографика
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 700,
      lineHeight: 1.3,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      lineHeight: 1.3,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
      lineHeight: 1.5,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    button: {
      fontSize: '0.875rem',
      fontWeight: 600,
      textTransform: 'none', // Убираем uppercase
    },
    caption: {
      fontSize: '0.75rem',
      lineHeight: 1.4,
    },
  },

  // Breakpoints (mobile-first)
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 900,
      lg: 1200,
      xl: 1536,
    },
  },

  // Spacing (8px base)
  spacing: 8,

  // Скругление углов
  shape: {
    borderRadius: 12,
  },

  // Тени
  shadows: [
    'none',
    '0px 2px 4px rgba(0, 0, 0, 0.05)',
    '0px 4px 8px rgba(0, 0, 0, 0.08)',
    '0px 8px 16px rgba(0, 0, 0, 0.10)',
    '0px 12px 24px rgba(0, 0, 0, 0.12)',
    '0px 16px 32px rgba(0, 0, 0, 0.14)',
    '0px 20px 40px rgba(0, 0, 0, 0.16)',
    '0px 24px 48px rgba(0, 0, 0, 0.18)',
    '0px 28px 56px rgba(0, 0, 0, 0.20)',
    '0px 32px 64px rgba(0, 0, 0, 0.22)',
    '0px 36px 72px rgba(0, 0, 0, 0.24)',
    '0px 40px 80px rgba(0, 0, 0, 0.26)',
    '0px 44px 88px rgba(0, 0, 0, 0.28)',
    '0px 48px 96px rgba(0, 0, 0, 0.30)',
    '0px 52px 104px rgba(0, 0, 0, 0.32)',
    '0px 56px 112px rgba(0, 0, 0, 0.34)',
    '0px 60px 120px rgba(0, 0, 0, 0.36)',
    '0px 64px 128px rgba(0, 0, 0, 0.38)',
    '0px 68px 136px rgba(0, 0, 0, 0.40)',
    '0px 72px 144px rgba(0, 0, 0, 0.42)',
    '0px 76px 152px rgba(0, 0, 0, 0.44)',
    '0px 80px 160px rgba(0, 0, 0, 0.46)',
    '0px 84px 168px rgba(0, 0, 0, 0.48)',
    '0px 88px 176px rgba(0, 0, 0, 0.50)',
    '0px 92px 184px rgba(0, 0, 0, 0.52)',
  ],

  // Настройка компонентов
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          // Отключаем pull-to-refresh и bounce на iOS
          overscrollBehavior: 'none',
          // Предотвращаем zoom на iOS при фокусе
          touchAction: 'manipulation',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '10px 20px',
          fontWeight: 600,
          // Улучшаем touch target на мобильных (минимум 44px)
          minHeight: 44,
        },
        sizeLarge: {
          padding: '12px 24px',
          fontSize: '1rem',
          minHeight: 48,
        },
        sizeSmall: {
          padding: '6px 16px',
          fontSize: '0.813rem',
          minHeight: 36,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.08)',
          // Улучшаем производительность на мобильных
          willChange: 'transform',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
          },
          // Фикс для iOS - минимум 16px font-size предотвращает zoom
          '& input': {
            fontSize: '1rem',
          },
        },
      },
    },
    MuiBottomNavigation: {
      styleOverrides: {
        root: {
          height: 64,
          borderTop: '1px solid #E5E7EB',
          // Фиксируем внизу на мобильных
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          zIndex: 1000,
          // Добавляем safe area для iPhone с вырезом
          paddingBottom: 'env(safe-area-inset-bottom)',
        },
      },
    },
    MuiBottomNavigationAction: {
      styleOverrides: {
        root: {
          minWidth: 60,
          // Улучшаем touch target
          minHeight: 64,
          '&.Mui-selected': {
            fontSize: '0.75rem',
          },
        },
      },
    },
    MuiContainer: {
      styleOverrides: {
        root: {
          // Добавляем safe area padding для iPhone
          paddingLeft: 'max(16px, env(safe-area-inset-left))',
          paddingRight: 'max(16px, env(safe-area-inset-right))',
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          // Минимальный размер touch target 44px
          minWidth: 44,
          minHeight: 44,
        },
      },
    },
  },
});

export default theme;
