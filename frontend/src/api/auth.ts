import apiClient from './client';
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  VerificationRequest,
  VerifyEmailRequest,
  VerificationCodeResponse,
} from '@/types';

// Регистрация
export const register = async (data: RegisterRequest) => {
  const response = await apiClient.post<{ 
    verification_token: string;
    email: string;
    message: string;
  }>('/auth/register', data);
  return response.data;
};

// Вход
export const login = async (data: LoginRequest) => {
  const response = await apiClient.post<TokenResponse>('/auth/login', data);
  return response.data;
};

// Запрос кода верификации
export const requestVerificationCode = async (data: VerificationRequest) => {
  const response = await apiClient.post<VerificationCodeResponse>(
    '/auth/request-verification-code',
    data
  );
  return response.data;
};

// Верификация email с кодом
export const verifyEmail = async (data: VerifyEmailRequest) => {
  const response = await apiClient.post<TokenResponse>('/auth/verify-email', data);
  return response.data;
};

// Обновление токенов
export const refreshTokens = async (refreshToken: string) => {
  const response = await apiClient.post<TokenResponse>('/auth/refresh', {
    refresh_token: refreshToken,
  });
  return response.data;
};

// Google OAuth: инициация входа
export const initiateGoogleLogin = async (frontendRedirectUri: string) => {
  const response = await apiClient.post<{ 
    authorization_url: string;
    message: string;
  }>(
    '/auth/google/login',
    { frontend_redirect_uri: frontendRedirectUri }
  );
  return response.data;
};

// Google OAuth: обмен одноразового токена на JWT
export const exchangeGoogleToken = async (token: string) => {
  const response = await apiClient.post<TokenResponse>(
    '/auth/google/exchange-token',
    { token }
  );
  return response.data;
};
