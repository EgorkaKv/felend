import apiClient from './client';
import type {
  Survey,
  SurveyFilters,
  CreateSurveyRequest,
  ParticipateResponse,
  VerifyParticipationResponse,
} from '@/types';

// Получить список всех опросов (лента)
export const getSurveys = async (filters?: SurveyFilters, page = 1, limit = 20) => {
  const params = new URLSearchParams();
  params.append('page', page.toString());
  params.append('limit', limit.toString());

  if (filters?.search) {
    params.append('search', filters.search);
  }
  if (filters?.category) {
    params.append('category', filters.category);
  }
  if (filters?.min_reward) {
    params.append('min_reward', filters.min_reward.toString());
  }
  if (filters?.max_reward) {
    params.append('max_reward', filters.max_reward.toString());
  }
  if (filters?.duration) {
    params.append('duration', filters.duration);
  }
  if (filters?.only_suitable !== undefined) {
    params.append('only_suitable', filters.only_suitable.toString());
  }

  const response = await apiClient.get<{
    surveys: Survey[];
    total: number;
    page: number;
    pages: number;
  }>(`/surveys?${params.toString()}`);
  return response.data;
};

// Получить мои опросы
export const getMySurveys = async (status?: string, page = 1, limit = 20) => {
  const params = new URLSearchParams();
  params.append('page', page.toString());
  params.append('limit', limit.toString());

  if (status && status !== 'all') {
    params.append('status', status);
  }

  const response = await apiClient.get<{
    surveys: Survey[];
    total: number;
    page: number;
    pages: number;
  }>(`/surveys/my/?${params.toString()}`);
  return response.data;
};

// Создать опрос
export const createSurvey = async (data: CreateSurveyRequest) => {
  const response = await apiClient.post<Survey>('/surveys/my/', data);
  return response.data;
};

// Начать прохождение опроса
export const participateInSurvey = async (surveyId: number) => {
  const response = await apiClient.post<ParticipateResponse>(`/surveys/${surveyId}/participate`);
  return response.data;
};

// Верифицировать прохождение опроса
export const verifyParticipation = async (surveyId: number) => {
  const response = await apiClient.post<VerifyParticipationResponse>(
    `/surveys/${surveyId}/verify`
  );
  return response.data;
};

// Приостановить опрос
export const pauseSurvey = async (surveyId: number) => {
  const response = await apiClient.post<{ message: string }>(`/surveys/my/${surveyId}/pause`);
  return response.data;
};

// Возобновить опрос
export const resumeSurvey = async (surveyId: number) => {
  const response = await apiClient.post<{ message: string }>(`/surveys/my/${surveyId}/resume`);
  return response.data;
};

// Удалить опрос
export const deleteSurvey = async (surveyId: number) => {
  const response = await apiClient.delete<{ message: string }>(`/surveys/my/${surveyId}`);
  return response.data;
};
