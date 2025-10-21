import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Container, Typography, Alert } from '@mui/material';
import { Email as EmailIcon } from '@mui/icons-material';
import Button from '@/components/Button';
import PinInput from '@/components/PinInput';
import { useAuth } from '@/hooks/useAuth';
import { useAppSelector } from '@/store/hooks';
import { requestVerificationCode } from '@/api/auth';

const RESEND_COOLDOWN = 60; // секунды

const ConfirmEmailPage = () => {
  const navigate = useNavigate();
  const { verifyEmail } = useAuth();
  const confirmationToken = useAppSelector((state) => state.auth.confirmationToken);

  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [timer, setTimer] = useState(RESEND_COOLDOWN);
  const [canResend, setCanResend] = useState(false);

  // Таймер для повторной отправки
  useEffect(() => {
    if (timer > 0) {
      const interval = setInterval(() => {
        setTimer((prev) => prev - 1);
      }, 1000);
      return () => clearInterval(interval);
    } else {
      setCanResend(true);
    }
  }, [timer]);

  // Автоматическая отправка кода при заполнении всех 6 цифр
  useEffect(() => {
    if (code.length === 6 && !loading) {
      handleSubmit();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [code]);

  // Проверка наличия confirmation token
  useEffect(() => {
    if (!confirmationToken) {
      navigate('/register', { replace: true });
    }
  }, [confirmationToken, navigate]);

  // Автоматическая отправка кода при загрузке страницы
  useEffect(() => {
    if (confirmationToken) {
      handleRequestCode();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSubmit = async () => {
    if (!confirmationToken) return;

    setLoading(true);
    setError('');

    try {
      await verifyEmail({
        confirmation_token: confirmationToken,
        code: code,
      });
    } catch {
      setError('Неверный код. Попробуйте еще раз.');
      setCode('');
    } finally {
      setLoading(false);
    }
  };

  const handleRequestCode = async () => {
    if (!confirmationToken || !canResend) return;

    try {
      await requestVerificationCode({ confirmation_token: confirmationToken });
      setTimer(RESEND_COOLDOWN);
      setCanResend(false);
      setError('');
    } catch {
      setError('Не удалось отправить код. Попробуйте позже.');
    }
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
          {/* Иконка */}
          <Box
            sx={{
              width: 80,
              height: 80,
              borderRadius: '50%',
              bgcolor: 'primary.main',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mb: 3,
            }}
          >
            <EmailIcon sx={{ fontSize: 40, color: 'white' }} />
          </Box>

          {/* Заголовок */}
          <Typography
            variant="h4"
            component="h1"
            gutterBottom
            sx={{ fontWeight: 600, mb: 1, textAlign: 'center' }}
          >
            Подтвердите email
          </Typography>

          {/* Описание */}
          <Typography
            variant="body1"
            color="text.secondary"
            align="center"
            sx={{ mb: 4, maxWidth: 400 }}
          >
            Мы отправили 6-значный код на вашу почту. Введите его ниже для подтверждения.
          </Typography>

          {/* Pin Input */}
          <Box sx={{ mb: 3 }}>
            <PinInput
              value={code}
              onChange={setCode}
              disabled={loading}
              error={!!error}
              autoFocus
            />
          </Box>

          {/* Ошибка */}
          {error && (
            <Alert severity="error" sx={{ mb: 3, width: '100%' }}>
              {error}
            </Alert>
          )}

          {/* Таймер и повторная отправка */}
          <Box sx={{ textAlign: 'center', mb: 2 }}>
            {!canResend ? (
              <Typography variant="body2" color="text.secondary">
                Отправить код повторно через {timer} сек
              </Typography>
            ) : (
              <Button variant="text" onClick={handleRequestCode}>
                Отправить код повторно
              </Button>
            )}
          </Box>

          {/* Кнопка назад */}
          <Button
            variant="outlined"
            fullWidth
            onClick={() => navigate('/register')}
            sx={{ mt: 2 }}
          >
            Назад к регистрации
          </Button>
        </Box>
      </Container>
    </Box>
  );
};

export default ConfirmEmailPage;
