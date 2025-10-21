// Типы для пользователей

export interface User {
  id: number;
  email: string;
  full_name: string;
  balance: number;
  respondent_code: string;
  demographic_data?: DemographicData;
  avatar_url?: string;
  created_at: string;
}

export interface DemographicData {
  age?: number;
  gender?: 'male' | 'female' | 'other';
  employment?: 'student' | 'employed' | 'unemployed' | 'self_employed';
  income?: 'low' | 'medium' | 'high';
  marital_status?: 'single' | 'married' | 'divorced' | 'widowed';
  occupation?: string;
  location?: string;
}

export interface UpdateUserRequest {
  full_name?: string;
  demographic_data?: DemographicData;
  avatar_url?: string;
}
