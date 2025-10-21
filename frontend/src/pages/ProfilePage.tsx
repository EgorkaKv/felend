import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import useSWR from 'swr';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Button,
  CircularProgress,
  Alert,
  TextField as MuiTextField,
  MenuItem,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';

import { logout } from '@/store/authSlice';
import { showSnackbar } from '@/store/uiSlice';
import { getCurrentUser, updateUser } from '@/api/users';
import { getGoogleAccounts, disconnectGoogleAccount } from '@/api/googleAccounts';
import type { RootState } from '@/store';
import type { UpdateUserRequest, GoogleAccount } from '@/types';

interface ProfileFormData {
  full_name: string;
  age?: number | '';
  gender?: 'male' | 'female' | 'other' | '';
  occupation?: string;
}

const profileSchema = yup.object().shape({
  full_name: yup.string().required('Имя обязательно'),
  gender: yup.string().oneOf(['male', 'female', 'other', '']).optional(),
  age: yup.number().min(13, 'Минимальный возраст 13 лет').max(120, 'Некорректный возраст').optional(),
  occupation: yup.string().max(100, 'Максимум 100 символов').optional(),
});

function ProfilePage() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const user = useSelector((state: RootState) => state.auth.user);
  const [activeTab, setActiveTab] = useState(0);
  const [connectDialogOpen, setConnectDialogOpen] = useState(false);
  const [googleEmail, setGoogleEmail] = useState('');
  const [saving, setSaving] = useState(false);

  const { data: userData, mutate: mutateUser } = useSWR('/users/me', getCurrentUser);
  const { data: googleData, mutate: mutateGoogle } = useSWR('/google-accounts', getGoogleAccounts);

  const googleAccounts = googleData?.accounts || [];

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProfileFormData>({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: yupResolver(profileSchema) as any,
    defaultValues: {
      full_name: userData?.full_name || '',
      gender: userData?.demographic_data?.gender || '',
      age: userData?.demographic_data?.age || '',
      occupation: userData?.demographic_data?.occupation || '',
    },
  });

  const onSubmit = async (data: ProfileFormData) => {
    setSaving(true);
    try {
      const updateData: UpdateUserRequest = {
        full_name: data.full_name,
        demographic_data: {
          gender: data.gender === '' ? undefined : data.gender,
          age: data.age === '' ? undefined : Number(data.age),
          occupation: data.occupation || undefined,
        },
      };

      await updateUser(updateData);
      mutateUser();
      dispatch(showSnackbar({ message: 'Профиль обновлен', severity: 'success' }));
    } catch {
      dispatch(showSnackbar({ message: 'Ошибка обновления профиля', severity: 'error' }));
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  const handleConnectGoogle = () => {
    // В реальном приложении здесь будет OAuth redirect
    dispatch(showSnackbar({ 
      message: 'OAuth интеграция с Google будет реализована на бэкенде', 
      severity: 'info' 
    }));
    setConnectDialogOpen(false);
  };

  const handleDisconnectGoogle = async (accountId: number) => {
    if (!window.confirm('Вы уверены, что хотите отключить этот Google аккаунт?')) {
      return;
    }

    try {
      await disconnectGoogleAccount(accountId);
      mutateGoogle();
      dispatch(showSnackbar({ message: 'Google аккаунт отключен', severity: 'success' }));
    } catch {
      dispatch(showSnackbar({ message: 'Ошибка отключения аккаунта', severity: 'error' }));
    }
  };

  if (!userData) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box mb={3}>
        <Typography variant="h5" fontWeight="bold" gutterBottom>
          Профиль
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {user?.email}
        </Typography>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(_e, newValue) => setActiveTab(newValue)}>
          <Tab label="Информация" />
          <Tab label="Google аккаунты" />
        </Tabs>
      </Box>

      {/* Tab 1: Profile Info */}
      {activeTab === 0 && (
        <Box component="form" onSubmit={handleSubmit(onSubmit)}>
          <Box display="flex" flexDirection="column" gap={2}>
            {/* Basic Info */}
            <MuiTextField
              label="Полное имя"
              {...register('full_name')}
              error={!!errors.full_name}
              helperText={errors.full_name?.message}
              fullWidth
            />

            <Divider sx={{ my: 1 }} />

            {/* Demographics */}
            <Typography variant="subtitle2" color="text.secondary">
              Демографические данные (опционально)
            </Typography>

            <MuiTextField
              select
              label="Пол"
              {...register('gender')}
              error={!!errors.gender}
              helperText={errors.gender?.message}
              fullWidth
            >
              <MenuItem value="">Не указан</MenuItem>
              <MenuItem value="male">Мужской</MenuItem>
              <MenuItem value="female">Женский</MenuItem>
              <MenuItem value="other">Другой</MenuItem>
            </MuiTextField>

            <MuiTextField
              type="number"
              label="Возраст"
              {...register('age')}
              error={!!errors.age}
              helperText={errors.age?.message}
              fullWidth
            />

            <MuiTextField
              label="Род занятий"
              {...register('occupation')}
              error={!!errors.occupation}
              helperText={errors.occupation?.message}
              fullWidth
            />

            <Box display="flex" gap={2} mt={2}>
              <Button
                type="submit"
                variant="contained"
                disabled={saving}
                fullWidth
              >
                {saving ? <CircularProgress size={24} /> : 'Сохранить'}
              </Button>
              <Button
                variant="outlined"
                color="error"
                onClick={handleLogout}
                fullWidth
              >
                Выйти
              </Button>
            </Box>
          </Box>
        </Box>
      )}

      {/* Tab 2: Google Accounts */}
      {activeTab === 1 && (
        <Box>
          <Box mb={2}>
            <Alert severity="info">
              Подключите Google аккаунты для создания опросов и прохождения других форм
            </Alert>
          </Box>

          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setConnectDialogOpen(true)}
            sx={{ mb: 2 }}
          >
            Подключить аккаунт
          </Button>

          {googleAccounts.length === 0 ? (
            <Alert severity="warning">Нет подключенных Google аккаунтов</Alert>
          ) : (
            <List>
              {googleAccounts.map((account: GoogleAccount) => (
                <ListItem
                  key={account.id}
                  sx={{
                    bgcolor: 'background.paper',
                    borderRadius: 2,
                    mb: 1,
                    border: '1px solid',
                    borderColor: 'divider',
                  }}
                >
                  <ListItemText
                    primary={account.email}
                    secondary={`Добавлен ${new Date(account.connected_at).toLocaleDateString('ru-RU')}`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      color="error"
                      onClick={() => handleDisconnectGoogle(account.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
        </Box>
      )}

      {/* Connect Google Dialog */}
      <Dialog open={connectDialogOpen} onClose={() => setConnectDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Подключить Google аккаунт</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            Введите email Google аккаунта, который вы будете использовать для опросов
          </Alert>
          <MuiTextField
            autoFocus
            label="Google Email"
            type="email"
            fullWidth
            value={googleEmail}
            onChange={(e) => setGoogleEmail(e.target.value)}
            placeholder="example@gmail.com"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConnectDialogOpen(false)}>Отмена</Button>
          <Button onClick={handleConnectGoogle} variant="contained">
            Подключить
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ProfilePage;
