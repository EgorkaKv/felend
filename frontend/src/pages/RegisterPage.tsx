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
  IconButton,
  InputAdornment,
} from '@mui/material';
import { Google as GoogleIcon, Visibility, VisibilityOff } from '@mui/icons-material';
import Button from '@/components/Button';
import TextField from '@/components/TextField';
import { useAuth } from '@/hooks/useAuth';
import type { RegisterRequest } from '@/types';

// Валидационная схема
const registerSchema = yup.object().shape({
  email: yup
    .string()
    .email('Введите корректный email')
    .required('Email обязателен'),
  password: yup
    .string()
    .min(6, 'Пароль должен быть не менее 6 символов')
    .required('Пароль обязателен'),
  confirmPassword: yup
    .string()
    .oneOf([yup.ref('password')], 'Пароли должны совпадать')
    .required('Подтвердите пароль'),
  full_name: yup
    .string()
    .min(2, 'Имя должно быть не менее 2 символов')
    .required('Имя обязательно'),
});

type RegisterFormData = {
  email: string;
  password: string;
  confirmPassword: string;
  full_name: string;
};

const RegisterPage = () => {
  const { register: registerUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: yupResolver(registerSchema),
    defaultValues: {
      email: '',
      password: '',
      confirmPassword: '',
      full_name: '',
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    setLoading(true);
    try {
      // Убираем confirmPassword перед отправкой
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { confirmPassword, ...registerData } = data;
      await registerUser(registerData as RegisterRequest);
    } catch {
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
            Создать аккаунт
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

          {/* Форма регистрации */}
          <Box
            component="form"
            onSubmit={handleSubmit(onSubmit)}
            sx={{ width: '100%' }}
          >
            {/* Имя */}
            <Controller
              name="full_name"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Полное имя"
                  fullWidth
                  error={!!errors.full_name}
                  helperText={errors.full_name?.message}
                  disabled={loading}
                  sx={{ mb: 2 }}
                />
              )}
            />

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

            {/* Подтверждение пароля */}
            <Controller
              name="confirmPassword"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Подтвердите пароль"
                  type={showConfirmPassword ? 'text' : 'password'}
                  fullWidth
                  error={!!errors.confirmPassword}
                  helperText={errors.confirmPassword?.message}
                  disabled={loading}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                          edge="end"
                        >
                          {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{ mb: 3 }}
                />
              )}
            />

            {/* Кнопка регистрации */}
            <Button
              type="submit"
              variant="primary"
              fullWidth
              loading={loading}
              sx={{ mb: 2 }}
            >
              Зарегистрироваться
            </Button>

            {/* Ссылка на вход */}
            <Typography variant="body2" align="center" color="text.secondary">
              Уже есть аккаунт?{' '}
              <Link component={RouterLink} to="/login" underline="hover">
                Войти
              </Link>
            </Typography>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};


export default RegisterPage;
