import { useNavigate } from 'react-router-dom';
import { useAppDispatch } from '@/store/hooks';
import { setTokens, setUser, setVerificationToken, logout as logoutAction } from '@/store/authSlice';
import { showSnackbar } from '@/store/uiSlice';
import * as authApi from '@/api/auth';
import * as usersApi from '@/api/users';
import type { LoginRequest, RegisterRequest, VerifyEmailRequest } from '@/types';
import { getErrorMessage, logError } from '@/utils/errorHandler';

export const useAuth = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  // Регистрация
  const register = async (data: RegisterRequest) => {
    try {
      if (import.meta.env.DEV) {
        console.log('%c[useAuth] Register attempt', 'color: #4D96FF; font-weight: bold', { email: data.email });
      }
      
      const response = await authApi.register(data);
      
      if (import.meta.env.DEV) {
        console.log('%c[useAuth] Register API success', 'color: #6BCF7F; font-weight: bold', {
          verification_token: response.verification_token ? '***' : undefined,
          email: response.email,
          message: response.message,
        });
      }
      
      // Сохраняем verification_token для верификации
      dispatch(setVerificationToken(response.verification_token));
      
      if (import.meta.env.DEV) {
        console.log('%c[useAuth] Verification token saved to Redux', 'color: #6BCF7F; font-weight: bold');
      }
      
      dispatch(
        showSnackbar({
          message: 'Регистрация успешна! Проверьте почту для подтверждения.',
          severity: 'success',
        })
      );
      
      if (import.meta.env.DEV) {
        console.log('%c[useAuth] Navigating to /confirm-email', 'color: #6BCF7F; font-weight: bold');
      }
      
      // Переходим на страницу подтверждения email
      navigate('/confirm-email');
      
      if (import.meta.env.DEV) {
        console.log('%c[useAuth] Navigation complete', 'color: #6BCF7F; font-weight: bold');
      }
      
      return response;
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      logError('Register', error);
      
      dispatch(showSnackbar({ message: errorMessage, severity: 'error' }));
      throw error;
    }
  };

  // Вход
  const login = async (data: LoginRequest) => {
    try {
      if (import.meta.env.DEV) {
        console.log('%c[useAuth] Login attempt', 'color: #4D96FF; font-weight: bold', { email: data.email });
      }
      
      const response = await authApi.login(data);
      
      if (import.meta.env.DEV) {
        console.log('%c[useAuth] Login API success', 'color: #6BCF7F; font-weight: bold', {
          access_token: response.access_token ? '***' : undefined,
          refresh_token: response.refresh_token ? '***' : undefined,
        });
      }
      
      // Сохраняем токены
      dispatch(
        setTokens({
          accessToken: response.access_token,
          refreshToken: response.refresh_token,
        })
      );
      
      if (import.meta.env.DEV) {
        console.log('%c[useAuth] Tokens saved to Redux', 'color: #6BCF7F; font-weight: bold');
      }
      
      // Получаем данные пользователя
      const user = await usersApi.getCurrentUser();
      
      if (import.meta.env.DEV) {
        console.log('%c[useAuth] User data fetched', 'color: #6BCF7F; font-weight: bold', {
          id: user.id,
          email: user.email,
        });
      }
      
      dispatch(setUser(user));
      
      dispatch(showSnackbar({ message: 'Успешный вход!', severity: 'success' }));
      
      // Переходим на главную
      navigate('/');
      
      return response;
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      logError('Login', error);
      
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
      const errorMessage = getErrorMessage(error);
      logError('VerifyEmail', error);
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
