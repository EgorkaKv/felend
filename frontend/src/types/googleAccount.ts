// Типы для Google аккаунтов

export interface GoogleAccount {
  id: number;
  email: string;
  name: string;
  avatar_url?: string;
  is_primary: boolean;
  connected_at: string;
}

export interface ConnectGoogleAccountRequest {
  code: string;
}
