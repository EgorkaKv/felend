// Базовые типы для API ответов

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
  limit: number;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
  skip?: number;
}
