// Базовые типы для API ответов

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

// Структура ошибки API согласно документации /docs/api/README.md
export interface ApiError {
  message: string;      // Human-readable error message
  code: string;         // ERROR_CODE (AUTH001, SURVEY001, etc.)
  type: string;         // ExceptionType
  details?: Record<string, unknown>;  // Additional context-specific information
  timestamp?: string;   // ISO 8601 timestamp
  path?: string;        // API endpoint path
}

// Обертка для ответа с ошибкой
export interface ApiErrorResponse {
  error: ApiError;
  detail?: string;      // Legacy format fallback
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
