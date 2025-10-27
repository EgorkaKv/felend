import axios from 'axios';
import type { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { store } from '@/store';
import { setTokens, logout } from '@/store/authSlice';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const IS_DEV = import.meta.env.DEV;

// Показываем подсказку при первой загрузке в dev mode
if (IS_DEV) {
  console.log(
    '%c🐛 Felend Debug Mode',
    'color: white; background: #4D96FF; padding: 8px 16px; border-radius: 4px; font-size: 14px; font-weight: bold;'
  );
  console.log(
    '%cДля отладки:\n' +
    '1. Откройте иконку 🐛 в правом нижнем углу\n' +
    '2. Все API запросы логируются в консоль\n' +
    '3. Подробнее: /QUICK-DEBUG.md',
    'color: #666; font-size: 12px;'
  );
  console.log('%cAPI URL:', 'color: #4D96FF; font-weight: bold', API_BASE_URL);
}

// Утилита для логирования в dev mode
const devLog = (type: 'request' | 'response' | 'error', message: string, data?: unknown) => {
  if (!IS_DEV) return;
  
  const styles = {
    request: 'color: #4D96FF; font-weight: bold',
    response: 'color: #6BCF7F; font-weight: bold',
    error: 'color: #FF6B6B; font-weight: bold',
  };
  
  console.log(`%c[API ${type.toUpperCase()}]`, styles[type], message);
  if (data) {
    console.log(data);
  }
};

// Создаем instance axios
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor - добавляем access token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const state = store.getState();
    const accessToken = state.auth.accessToken;

    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    // Dev logging
    devLog('request', `${config.method?.toUpperCase()} ${config.url}`, {
      headers: config.headers,
      data: config.data,
      params: config.params,
    });

    return config;
  },
  (error) => {
    devLog('error', 'Request interceptor error', error);
    return Promise.reject(error);
  }
);

// Response interceptor - обработка ошибок и refresh token
apiClient.interceptors.response.use(
  (response) => {
    // Dev logging
    devLog('response', `${response.status} ${response.config.url}`, {
      data: response.data,
      headers: response.headers,
    });
    
    return response;
  },
  async (error: AxiosError) => {
    // Dev logging для ошибок
    devLog('error', `${error.response?.status || 'Network Error'} ${error.config?.url}`, {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      headers: error.response?.headers,
    });

    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Если 401 и это не повторный запрос
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const state = store.getState();
      const refreshToken = state.auth.refreshToken;

      if (refreshToken) {
        try {
          devLog('request', 'Attempting token refresh...');
          
          // Попытка обновить access token
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = response.data;
          
          devLog('response', 'Token refresh successful', { access_token: '***', refresh_token: '***' });

          // Сохраняем новые токены
          store.dispatch(setTokens({ accessToken: access_token, refreshToken: refresh_token }));

          // Повторяем оригинальный запрос с новым токеном
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          return apiClient(originalRequest);
        } catch (refreshError) {
          devLog('error', 'Token refresh failed', refreshError);
          
          // Refresh token тоже не валиден - разлогиниваем
          store.dispatch(logout());
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        devLog('error', 'No refresh token available, redirecting to login');
        
        // Нет refresh token - редирект на логин
        store.dispatch(logout());
        window.location.href = '/login';
      }
    }

    // Если 403 - нет доступа
    if (error.response?.status === 403) {
      console.error('Access forbidden:', error.response.data);
    }

    // Если 500 - ошибка сервера
    if (error.response?.status === 500) {
      console.error('Server error:', error.response.data);
    }

    return Promise.reject(error);
  }
);

export default apiClient;
