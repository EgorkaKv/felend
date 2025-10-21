import apiClient from './client';
import type { GoogleAccount, ConnectGoogleAccountRequest } from '@/types';

// Получить список Google аккаунтов
export const getGoogleAccounts = async () => {
  const response = await apiClient.get<{ accounts: GoogleAccount[] }>('/google-accounts');
  return response.data;
};

// Подключить Google аккаунт (после OAuth callback)
export const connectGoogleAccount = async (data: ConnectGoogleAccountRequest) => {
  const response = await apiClient.post<{ account: GoogleAccount }>(
    '/google-accounts/connect',
    data
  );
  return response.data;
};

// Сделать аккаунт основным
export const setPrimaryGoogleAccount = async (accountId: number) => {
  const response = await apiClient.put<{ message: string }>(
    `/google-accounts/${accountId}/set-primary`
  );
  return response.data;
};

// Отключить Google аккаунт
export const disconnectGoogleAccount = async (accountId: number) => {
  const response = await apiClient.delete<{ message: string }>(`/google-accounts/${accountId}`);
  return response.data;
};
