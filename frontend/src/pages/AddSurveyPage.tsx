import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import useSWR from 'swr';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormHelperText from '@mui/material/FormHelperText';
import Divider from '@mui/material/Divider';
import Chip from '@mui/material/Chip';
import Alert from '@mui/material/Alert';
import { Add as AddIcon } from '@mui/icons-material';
import Button from '@/components/Button';
import TextField from '@/components/TextField';
import { createSurvey } from '@/api/surveys';
import { getGoogleAccounts } from '@/api/googleAccounts';
import { getCategories } from '@/api/categories';
import { useAppDispatch } from '@/store/hooks';
import { showSnackbar } from '@/store/uiSlice';
import { getErrorMessage } from '@/utils/errorHandler';
import type { CreateSurveyRequest, GoogleAccount, Category } from '@/types';

// Валидационная схема
const surveySchema = yup.object().shape({
  google_form_url: yup
    .string()
    .url('Введите корректный URL')
    .matches(
      /^https:\/\/docs\.google\.com\/forms/,
      'URL должен быть ссылкой на Google Form'
    )
    .required('Google Form URL обязателен'),
  google_account_id: yup.number().min(1, 'Выберите Google аккаунт').required('Google аккаунт обязателен'),
  category: yup.string().required('Категория обязательна'),
  theme_color: yup.string().required('Цвет темы обязателен'),
  reward: yup.number().min(0, 'Награда не может быть отрицательной').optional(),
  responses_needed: yup.number().min(1, 'Минимум 1 ответ').optional(),
  max_responses_per_user: yup.number().min(1, 'Минимум 1').max(5, 'Максимум 5').optional(),
});

type SurveyFormData = {
  google_form_url: string;
  google_account_id: number;
  category: string;
  theme_color: string;
  reward?: number;
  responses_needed?: number;
  max_responses_per_user?: number;
};

const themeColors = [
  { value: '#E3F2FD', label: 'Голубой', color: '#E3F2FD' },
  { value: '#F3E5F5', label: 'Фиолетовый', color: '#F3E5F5' },
  { value: '#E8F5E9', label: 'Зелёный', color: '#E8F5E9' },
  { value: '#FFF3E0', label: 'Оранжевый', color: '#FFF3E0' },
  { value: '#FCE4EC', label: 'Розовый', color: '#FCE4EC' },
  { value: '#F5F5F5', label: 'Серый', color: '#F5F5F5' },
];

const AddSurveyPage = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [loading, setLoading] = useState(false);

  // Получение Google аккаунтов
  const { data: googleAccountsData } = useSWR('/google-accounts', async () => {
    const data = await getGoogleAccounts();
    return data.google_accounts;
  });
  const googleAccounts = useMemo(
    () => googleAccountsData || [],
    [googleAccountsData]
  );

  // Получение категорий
  const { data: categoriesData } = useSWR('/categories', async () => {
    const data = await getCategories();
    return data.categories;
  });
  const categories = categoriesData || [];

  const {
    control,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<SurveyFormData>({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: yupResolver(surveySchema) as any,
    defaultValues: {
      google_form_url: '',
      google_account_id: 0,
      category: '',
      theme_color: themeColors[0].value,
      reward: undefined,
      responses_needed: undefined,
      max_responses_per_user: 1,
    },
  });

  // Автоматический выбор первого Google аккаунта
  useEffect(() => {
    if (googleAccounts.length > 0 && !errors.google_account_id) {
      setValue('google_account_id', googleAccounts[0].id);
    }
  }, [googleAccounts, setValue, errors.google_account_id]);

  const onSubmit = async (data: SurveyFormData) => {
    setLoading(true);

    try {
      const requestData: CreateSurveyRequest = {
        google_form_url: data.google_form_url,
        google_account_id: data.google_account_id,
        category: data.category,
        theme_color: data.theme_color,
        reward: data.reward,
        responses_needed: data.responses_needed,
        max_responses_per_user: data.max_responses_per_user,
      };

      await createSurvey(requestData);

      dispatch(
        showSnackbar({
          message: 'Опрос успешно создан!',
          severity: 'success',
        })
      );

      navigate('/my-surveys');
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      dispatch(showSnackbar({ message: errorMessage, severity: 'error' }));
    } finally {
      setLoading(false);
    }
  };

  // Проверка наличия Google аккаунтов
  if (googleAccounts.length === 0) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="body1" gutterBottom>
            Для создания опроса необходимо подключить Google аккаунт
          </Typography>
          <Button
            variant="primary"
            onClick={() => navigate('/profile/google-accounts')}
            sx={{ mt: 2 }}
          >
            Подключить Google аккаунт
          </Button>
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
          Создать опрос
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Создайте Google Form и разместите его на платформе
        </Typography>
      </Box>

      <Paper component="form" onSubmit={handleSubmit(onSubmit)} sx={{ p: 3 }}>
        {/* Google Form URL */}
        <Box sx={{ mb: 3 }}>
          <Controller
            name="google_form_url"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Ссылка на Google Form"
                placeholder="https://docs.google.com/forms/d/..."
                fullWidth
                error={!!errors.google_form_url}
                helperText={
                  errors.google_form_url?.message ||
                  'Скопируйте ссылку из Google Forms'
                }
                disabled={loading}
              />
            )}
          />
        </Box>

        {/* Google Account */}
        <Box sx={{ mb: 3 }}>
          <Controller
            name="google_account_id"
            control={control}
            render={({ field }) => (
              <FormControl fullWidth error={!!errors.google_account_id}>
                <InputLabel>Google аккаунт</InputLabel>
                <Select {...field} label="Google аккаунт" disabled={loading}>
                  {googleAccounts.map((account: GoogleAccount) => (
                    <MenuItem key={account.id} value={account.id}>
                      {account.email}
                      {account.is_primary && (
                        <Chip label="Основной" size="small" sx={{ ml: 1 }} />
                      )}
                    </MenuItem>
                  ))}
                </Select>
                {errors.google_account_id && (
                  <FormHelperText>{errors.google_account_id.message}</FormHelperText>
                )}
              </FormControl>
            )}
          />
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Категория */}
        <Box sx={{ mb: 3 }}>
          <Controller
            name="category"
            control={control}
            render={({ field }) => (
              <FormControl fullWidth error={!!errors.category}>
                <InputLabel>Категория</InputLabel>
                <Select {...field} label="Категория" disabled={loading}>
                  {categories.map((cat: Category) => (
                    <MenuItem key={cat.id} value={cat.id}>
                      {cat.name}
                    </MenuItem>
                  ))}
                </Select>
                {errors.category && (
                  <FormHelperText>{errors.category.message}</FormHelperText>
                )}
              </FormControl>
            )}
          />
        </Box>

        {/* Цвет темы */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Цвет карточки
          </Typography>
          <Controller
            name="theme_color"
            control={control}
            render={({ field }) => (
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {themeColors.map((color) => (
                  <Box
                    key={color.value}
                    onClick={() => field.onChange(color.value)}
                    sx={{
                      width: 60,
                      height: 60,
                      borderRadius: 2,
                      bgcolor: color.color,
                      border: 2,
                      borderColor:
                        field.value === color.value ? 'primary.main' : 'transparent',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      '&:hover': {
                        transform: 'scale(1.1)',
                      },
                    }}
                  />
                ))}
              </Box>
            )}
          />
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Дополнительные настройки */}
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
          Дополнительные настройки
        </Typography>

        <Box sx={{ mb: 3 }}>
          <Controller
            name="reward"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Дополнительная награда (баллов)"
                type="number"
                fullWidth
                error={!!errors.reward}
                helperText={
                  errors.reward?.message ||
                  'Опционально. Увеличивает минимальную награду за опрос'
                }
                disabled={loading}
              />
            )}
          />
        </Box>

        <Box sx={{ mb: 3 }}>
          <Controller
            name="responses_needed"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Необходимое количество ответов"
                type="number"
                fullWidth
                error={!!errors.responses_needed}
                helperText={
                  errors.responses_needed?.message ||
                  'Опционально. Опрос закроется после достижения этого числа'
                }
                disabled={loading}
              />
            )}
          />
        </Box>

        <Box sx={{ mb: 4 }}>
          <Controller
            name="max_responses_per_user"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Макс. количество ответов от 1 пользователя"
                type="number"
                fullWidth
                error={!!errors.max_responses_per_user}
                helperText={
                  errors.max_responses_per_user?.message ||
                  'По умолчанию: 1. Максимум: 5'
                }
                disabled={loading}
              />
            )}
          />
        </Box>

        {/* Кнопки */}
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            fullWidth
            onClick={() => navigate('/')}
            disabled={loading}
          >
            Отмена
          </Button>
          <Button
            type="submit"
            variant="primary"
            fullWidth
            loading={loading}
            startIcon={<AddIcon />}
          >
            Создать опрос
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default AddSurveyPage;
