import { useEffect, useState, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import { CheckCircle as CheckIcon, Error as ErrorIcon } from '@mui/icons-material';
import Button from '@/components/Button';
import { exchangeGoogleToken } from '@/api/auth';
import { useAppDispatch } from '@/store/hooks';
import { setTokens, setUser } from '@/store/authSlice';
import { getErrorMessage } from '@/utils/errorHandler';

type Status = 'loading' | 'success' | 'error';

const GoogleCallbackPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const dispatch = useAppDispatch();
  
  const [status, setStatus] = useState<Status>('loading');
  const [errorMessage, setErrorMessage] = useState('');
  
  // Используем ref для отслеживания выполнения запроса
  const hasProcessed = useRef(false);

  useEffect(() => {
    // Защита от повторного выполнения
    if (hasProcessed.current) {
      return;
    }

    const handleCallback = async () => {
      try {
        // Получаем токен из URL
        const token = searchParams.get('token');

        if (!token) {
          throw new Error('Токен не найден в URL');
        }

        // Помечаем что начали обработку
        hasProcessed.current = true;

        if (import.meta.env.DEV) {
          console.log('%c[GoogleCallback] Processing token...', 'color: #4D96FF; font-weight: bold');
        }

        // Обмениваем одноразовый токен на JWT
        const data = await exchangeGoogleToken(token);

        if (import.meta.env.DEV) {
          console.log('%c[GoogleCallback] Token exchanged successfully', 'color: #6BCF7F; font-weight: bold');
        }

        // Сохраняем JWT в Redux
        dispatch(setTokens({
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
        }));
        dispatch(setUser(data.user));

        // Показываем успех
        setStatus('success');

        // Редиректим на главную через 1 секунду
        setTimeout(() => {
          navigate('/', { replace: true });
        }, 1000);
      } catch (error) {
        console.error('Google OAuth callback error:', error);
        setStatus('error');
        setErrorMessage(getErrorMessage(error));
      }
    };

    handleCallback();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Пустой массив зависимостей - выполняется только один раз при монтировании

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          py: 4,
        }}
      >
        {status === 'loading' && (
          <>
            <CircularProgress size={64} sx={{ mb: 3 }} />
            <Typography variant="h5" fontWeight="bold" gutterBottom>
              Вход через Google...
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Пожалуйста, подождите
            </Typography>
          </>
        )}

        {status === 'success' && (
          <>
            <Box
              sx={{
                width: 80,
                height: 80,
                borderRadius: '50%',
                bgcolor: 'success.main',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 3,
              }}
            >
              <CheckIcon sx={{ fontSize: 48, color: 'white' }} />
            </Box>
            <Typography variant="h5" fontWeight="bold" gutterBottom>
              Успешный вход!
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Перенаправляем вас на главную...
            </Typography>
          </>
        )}

        {status === 'error' && (
          <>
            <Box
              sx={{
                width: 80,
                height: 80,
                borderRadius: '50%',
                bgcolor: 'error.main',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 3,
              }}
            >
              <ErrorIcon sx={{ fontSize: 48, color: 'white' }} />
            </Box>
            <Typography variant="h5" fontWeight="bold" gutterBottom>
              Ошибка авторизации
            </Typography>
            <Alert severity="error" sx={{ mt: 2, mb: 3, width: '100%' }}>
              {errorMessage || 'Не удалось войти через Google. Попробуйте еще раз.'}
            </Alert>
            <Box sx={{ display: 'flex', gap: 2, width: '100%' }}>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => navigate('/login')}
              >
                Вход
              </Button>
              <Button
                variant="primary"
                fullWidth
                onClick={() => navigate('/register')}
              >
                Регистрация
              </Button>
            </Box>
          </>
        )}
      </Box>
    </Container>
  );
};

export default GoogleCallbackPage;
