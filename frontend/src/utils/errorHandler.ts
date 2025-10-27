import axios from 'axios';
import type { ApiErrorResponse } from '@/types/api';

/**
 * Извлекает человекочитаемое сообщение об ошибке из различных источников
 * Приоритеты:
 * 1. error.message - новый формат API (согласно /docs/api/README.md)
 * 2. detail - старый формат для совместимости
 * 3. Network errors - специальная обработка
 * 4. HTTP status - если ничего другого нет
 * 5. Generic fallback
 * 
 * @param error - Объект ошибки (обычно из axios)
 * @returns Человекочитаемое сообщение об ошибке
 */
export const getErrorMessage = (error: unknown): string => {
  // Проверяем, является ли это Axios ошибкой
  if (axios.isAxiosError(error)) {
    // Приоритет 1: Данные из response.data
    if (error.response?.data) {
      const errorData = error.response.data as ApiErrorResponse;
      
      // Новый формат API: error.message
      if (errorData.error?.message) {
        return errorData.error.message;
      }
      
      // Старый формат: detail (для совместимости)
      if (errorData.detail) {
        return errorData.detail;
      }
    }
    
    // Приоритет 2: Network errors
    if (error.code === 'ERR_NETWORK') {
      return 'Network error. Please check your connection';
    }
    
    // Приоритет 3: HTTP статус ошибки
    if (error.response?.status) {
      const status = error.response.status;
      
      switch (status) {
        case 401:
          return 'User not authenticated';
        case 403:
          return 'Access forbidden';
        case 404:
          return 'Resource not found';
        case 500:
          return 'Internal server error';
        default:
          return `Request failed with status ${status}`;
      }
    }
    
    // Приоритет 4: Axios error message
    if (error.message) {
      return error.message;
    }
  }
  
  // Приоритет 5: Generic fallback
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An error occurred';
};

/**
 * Логирует детальную информацию об ошибке в dev режиме
 * @param context - Контекст где произошла ошибка (например, 'Login', 'Register')
 * @param error - Объект ошибки
 */
export const logError = (context: string, error: unknown): void => {
  if (import.meta.env.DEV) {
    if (axios.isAxiosError(error)) {
      console.error(`%c[${context.toUpperCase()} ERROR]`, 'color: #FF6B6B; font-weight: bold', {
        message: getErrorMessage(error),
        status: error.response?.status,
        code: error.code,
        data: error.response?.data,
        url: error.config?.url,
        method: error.config?.method,
      });
    } else {
      console.error(`%c[${context.toUpperCase()} ERROR]`, 'color: #FF6B6B; font-weight: bold', error);
    }
  }
};
