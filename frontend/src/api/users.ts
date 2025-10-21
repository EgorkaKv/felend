import apiClient from './client';
import type { User, UpdateUserRequest, Transaction, TransactionFilters } from '@/types';

// Получить информацию о текущем пользователе
export const getCurrentUser = async () => {
  const response = await apiClient.get<User>('/users/me');
  return response.data;
};

// Обновить профиль пользователя
export const updateUser = async (data: UpdateUserRequest) => {
  const response = await apiClient.put<User>('/users/me', data);
  return response.data;
};

// Получить транзакции пользователя
export const getUserTransactions = async (filters?: TransactionFilters, page = 1, limit = 20) => {
  const params = new URLSearchParams();
  params.append('page', page.toString());
  params.append('limit', limit.toString());
  
  if (filters?.type && filters.type !== 'all') {
    params.append('type', filters.type);
  }

  const response = await apiClient.get<{
    transactions: Transaction[];
    total: number;
    page: number;
    pages: number;
  }>(`/users/me/transactions?${params.toString()}`);
  return response.data;
};
