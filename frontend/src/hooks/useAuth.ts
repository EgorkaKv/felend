import { useNavigate } from 'react-router-dom';
import { useAppDispatch } from '@/store/hooks';
import { setTokens, setUser, setConfirmationToken, logout as logoutAction } from '@/store/authSlice';
import { showSnackbar } from '@/store/uiSlice';
import * as authApi from '@/api/auth';
import * as usersApi from '@/api/users';
import type { LoginRequest, RegisterRequest, VerifyEmailRequest } from '@/types';

// Хелпер для извлечения сообщения об ошибке
const getErrorMessage = (error: unknown, defaultMessage: string): string => {
  if (error && typeof error === 'object' && 'response' in error) {
    const response = (error as { response?: { data?: { message?: string } } }).response;
    return response?.data?.message || defaultMessage;
  }
  return defaultMessage;
};

export const useAuth = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  // Регистрация
  const register = async (data: RegisterRequest) => {
    try {
      const response = await authApi.register(data);
      
      // Сохраняем confirmation_token для верификации
      dispatch(setConfirmationToken(response.confirmation_token));
      
      dispatch(
        showSnackbar({
          message: 'Регистрация успешна! Проверьте почту для подтверждения.',
          severity: 'success',
        })
      );
      
      // Переходим на страницу подтверждения email
      navigate('/confirm-email');
      
      return response;
    } catch (error) {
      const errorMessage = getErrorMessage(error, 'Ошибка регистрации');
      dispatch(showSnackbar({ message: errorMessage, severity: 'error' }));
      throw error;
    }
  };

  // Вход
  const login = async (data: LoginRequest) => {
    try {
      const response = await authApi.login(data);
      
      // Сохраняем токены
      dispatch(
        setTokens({
          accessToken: response.access_token,
          refreshToken: response.refresh_token,
        })
      );
      
      // Получаем данные пользователя
      const user = await usersApi.getCurrentUser();
      dispatch(setUser(user));
      
      dispatch(showSnackbar({ message: 'Успешный вход!', severity: 'success' }));
      
      // Переходим на главную
      navigate('/');
      
      return response;
    } catch (error) {
      const errorMessage = getErrorMessage(error, 'Ошибка входа');
      dispatch(showSnackbar({ message: errorMessage, severity: 'error' }));
      throw error;
    }
  };

  // Верификация email
  const verifyEmail = async (data: VerifyEmailRequest) => {
    try {
      const response = await authApi.verifyEmail(data);
      
      // Сохраняем токены
      dispatch(
        setTokens({
          accessToken: response.access_token,
          refreshToken: response.refresh_token,
        })
      );
      
      // Получаем данные пользователя
      const user = await usersApi.getCurrentUser();
      dispatch(setUser(user));
      
      dispatch(
        showSnackbar({
          message: 'Email подтвержден! Добро пожаловать!',
          severity: 'success',
        })
      );
      
      // Переходим на главную
      navigate('/');
      
      return response;
    } catch (error) {
      const errorMessage = getErrorMessage(error, 'Неверный код');
      dispatch(showSnackbar({ message: errorMessage, severity: 'error' }));
      throw error;
    }
  };

  // Выход
  const logout = () => {
    dispatch(logoutAction());
    dispatch(showSnackbar({ message: 'Вы вышли из системы', severity: 'info' }));
    navigate('/login');
  };

  return {
    register,
    login,
    verifyEmail,
    logout,
  };
};
