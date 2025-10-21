import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import useSWR from 'swr';
import {
  Container,
  Box,
  Typography,
  Paper,
  Alert,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import {
  OpenInNew as OpenIcon,
  CheckCircle as CheckIcon,
  Assignment as SurveyIcon,
} from '@mui/icons-material';
import Button from '@/components/Button';
import Loader from '@/components/Loader';
import { participateInSurvey, verifyParticipation } from '@/api/surveys';
import { useAppDispatch } from '@/store/hooks';
import { updateUserBalance } from '@/store/authSlice';
import { showSnackbar } from '@/store/uiSlice';
import type { Survey } from '@/types';
import apiClient from '@/api/client';

const steps = ['Откройте опрос', 'Заполните форму', 'Подтвердите прохождение'];

const SurveyCompletionPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();

  const [activeStep, setActiveStep] = useState(0);
  const [googleFormUrl, setGoogleFormUrl] = useState<string | null>(null);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Получение информации об опросе
  const { data: survey, isLoading } = useSWR<Survey>(
    id ? `/surveys/${id}` : null,
    async () => {
      const response = await apiClient.get<Survey>(`/surveys/${id}`);
      return response.data;
    }
  );

  // Автоматическое начало участия при загрузке страницы
  useEffect(() => {
    if (survey && !googleFormUrl && activeStep === 0) {
      handleStartParticipation();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [survey]);

  const handleStartParticipation = async () => {
    if (!id) return;

    try {
      const response = await participateInSurvey(Number(id));
      setGoogleFormUrl(response.google_form_url);
      setActiveStep(1);
      // Открываем форму в новой вкладке
      window.open(response.google_form_url, '_blank');
    } catch {
      setError('Не удалось начать участие в опросе');
      dispatch(
        showSnackbar({
          message: 'Ошибка при начале участия в опросе',
          severity: 'error',
        })
      );
    }
  };

  const handleOpenForm = () => {
    if (googleFormUrl) {
      window.open(googleFormUrl, '_blank');
    }
  };

  const handleVerify = async () => {
    if (!id) return;

    setVerifying(true);
    setError(null);

    try {
      const response = await verifyParticipation(Number(id));

      if (response.success) {
        // Успешная верификация
        setActiveStep(2);

        // Обновляем баланс
        if (response.new_balance !== undefined) {
          dispatch(updateUserBalance(response.new_balance));
        }

        // Показываем успешное сообщение
        dispatch(
          showSnackbar({
            message: `Поздравляем! Вы получили +${response.reward} баллов!`,
            severity: 'success',
          })
        );

        // Перенаправляем на главную через 2 секунды
        setTimeout(() => {
          navigate('/', { replace: true });
        }, 2000);
      } else {
        setError(response.message || 'Не удалось подтвердить прохождение');
      }
    } catch (err: unknown) {
      const errorMessage =
        err && typeof err === 'object' && 'response' in err
          ? ((err as { response?: { data?: { message?: string } } }).response?.data
              ?.message as string)
          : 'Не удалось подтвердить прохождение';

      setError(errorMessage);
      dispatch(showSnackbar({ message: errorMessage, severity: 'error' }));
    } finally {
      setVerifying(false);
    }
  };

  if (isLoading) {
    return <Loader />;
  }

  if (!survey) {
    return (
      <Container maxWidth="sm" sx={{ py: 4 }}>
        <Alert severity="error">Опрос не найден</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {/* Информация об опросе */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <SurveyIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
          <Box>
            <Typography variant="h5" component="h1" sx={{ fontWeight: 600 }}>
              {survey.title}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Награда: +{survey.reward} баллов
            </Typography>
          </Box>
        </Box>

        {/* Stepper */}
        <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {/* Ошибка */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Контент в зависимости от шага */}
        {activeStep === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Загружаем опрос...
            </Typography>
          </Box>
        )}

        {activeStep === 1 && (
          <Box sx={{ textAlign: 'center', py: 2 }}>
            <Typography variant="h6" gutterBottom>
              Заполните опрос в открывшейся вкладке
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              После заполнения Google Form вернитесь на эту страницу и подтвердите
              прохождение
            </Typography>

            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
              <Button
                variant="outlined"
                startIcon={<OpenIcon />}
                onClick={handleOpenForm}
              >
                Открыть опрос снова
              </Button>
              <Button
                variant="primary"
                startIcon={<CheckIcon />}
                onClick={handleVerify}
                loading={verifying}
              >
                Подтвердить прохождение
              </Button>
            </Box>

            <Alert severity="info" sx={{ mt: 3 }}>
              <Typography variant="body2">
                <strong>Важно:</strong> Используйте тот же Google аккаунт, который
                привязан к вашему профилю Felend
              </Typography>
            </Alert>
          </Box>
        )}

        {activeStep === 2 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <CheckIcon sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
              Отлично!
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
              Вы успешно прошли опрос и получили +{survey.reward} баллов
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Перенаправление на главную страницу...
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Кнопка назад */}
      {activeStep < 2 && (
        <Button variant="outlined" fullWidth onClick={() => navigate('/')}>
          Вернуться на главную
        </Button>
      )}
    </Container>
  );
};

export default SurveyCompletionPage;
