import { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import {
  Box,
  Container,
  Typography,
  Link,
  Divider,
  FormControlLabel,
  Checkbox,
  IconButton,
  InputAdornment,
} from '@mui/material';
import { Google as GoogleIcon, Visibility, VisibilityOff } from '@mui/icons-material';
import Button from '@/components/Button';
import TextField from '@/components/TextField';
import { useAuth } from '@/hooks/useAuth';

// Валидационная схема
const loginSchema = yup.object().shape({
  email: yup
    .string()
    .email('Введите корректный email')
    .required('Email обязателен'),
  password: yup.string().required('Пароль обязателен'),
  rememberMe: yup.boolean().default(false),
});

type LoginFormData = {
  email: string;
  password: string;
  rememberMe: boolean;
};

const LoginPage = () => {
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: yupResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false,
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setLoading(true);
    try {
      if (import.meta.env.DEV) {
        console.log('%c[LOGIN ATTEMPT]', 'color: #4D96FF; font-weight: bold', {
          email: data.email,
          password: '***',
          rememberMe: data.rememberMe,
        });
      }
      
      await login({
        email: data.email,
        password: data.password,
      });
      
      if (import.meta.env.DEV) {
        console.log('%c[LOGIN SUCCESS]', 'color: #6BCF7F; font-weight: bold');
      }
      
      // TODO: Обработать rememberMe если нужно
    } catch (error) {
      if (import.meta.env.DEV) {
        console.error('%c[LOGIN ERROR]', 'color: #FF6B6B; font-weight: bold', error);
      }
      // Ошибки обрабатываются в useAuth hook
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    // Редирект на бэкенд для Google OAuth
    window.location.href = `${import.meta.env.VITE_API_BASE_URL}/auth/google/login`;
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        bgcolor: 'background.default',
        py: 4,
      }}
    >
      <Container maxWidth="sm">
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          {/* Логотип */}
          <Typography
            variant="h3"
            component="h1"
            gutterBottom
            sx={{
              fontWeight: 700,
              color: 'primary.main',
              mb: 1,
            }}
          >
            Felend
          </Typography>

          {/* Заголовок */}
          <Typography
            variant="h5"
            component="h2"
            gutterBottom
            sx={{ fontWeight: 600, mb: 3 }}
          >
            Вход в аккаунт
          </Typography>

          {/* Google кнопка */}
          <Button
            variant="outlined"
            fullWidth
            onClick={handleGoogleLogin}
            startIcon={<GoogleIcon />}
            sx={{ mb: 3 }}
          >
            Войти через Google
          </Button>

          {/* Разделитель */}
          <Divider sx={{ width: '100%', mb: 3 }}>
            <Typography variant="body2" color="text.secondary">
              или
            </Typography>
          </Divider>

          {/* Форма входа */}
          <Box
            component="form"
            onSubmit={handleSubmit(onSubmit)}
            sx={{ width: '100%' }}
          >
            {/* Email */}
            <Controller
              name="email"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Email"
                  type="email"
                  fullWidth
                  error={!!errors.email}
                  helperText={errors.email?.message}
                  disabled={loading}
                  sx={{ mb: 2 }}
                />
              )}
            />

            {/* Пароль */}
            <Controller
              name="password"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Пароль"
                  type={showPassword ? 'text' : 'password'}
                  fullWidth
                  error={!!errors.password}
                  helperText={errors.password?.message}
                  disabled={loading}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{ mb: 2 }}
                />
              )}
            />

            {/* Remember Me */}
            <Controller
              name="rememberMe"
              control={control}
              render={({ field }) => (
                <FormControlLabel
                  control={<Checkbox {...field} checked={field.value} />}
                  label="Запомнить меня"
                  sx={{ mb: 3 }}
                />
              )}
            />

            {/* Кнопка входа */}
            <Button
              type="submit"
              variant="primary"
              fullWidth
              loading={loading}
              sx={{ mb: 2 }}
            >
              Войти
            </Button>

            {/* Ссылка на регистрацию */}
            <Typography variant="body2" align="center" color="text.secondary">
              Нет аккаунта?{' '}
              <Link component={RouterLink} to="/register" underline="hover">
                Зарегистрироваться
              </Link>
            </Typography>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default LoginPage;
