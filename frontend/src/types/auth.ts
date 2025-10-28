// Типы для аутентификации

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: number;
    email: string;
    full_name: string;
    balance: number;
    respondent_code: string;
    created_at: string;
  };
}

export interface VerificationRequest {
  verification_token: string;
}

export interface VerifyEmailRequest {
  verification_token: string;
  code: string;
}

export interface VerificationCodeResponse {
  message: string;
  expires_at: string;
}
