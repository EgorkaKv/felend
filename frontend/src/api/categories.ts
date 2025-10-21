import apiClient from './client';
import type { Category } from '@/types';

// Получить список категорий опросов
export const getCategories = async () => {
  const response = await apiClient.get<{ categories: Category[] }>('/categories');
  return response.data;
};
