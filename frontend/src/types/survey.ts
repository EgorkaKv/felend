// Типы для опросов

export interface Survey {
  id: number;
  title: string;
  description: string;
  google_form_url: string;
  reward: number;
  minimum_reward: number;
  questions_count: number;
  estimated_time: number; // в минутах
  category: string;
  theme_color: string;
  criteria?: SurveyCriteria;
  responses_count: number;
  responses_needed?: number;
  max_responses_per_user: number;
  status: 'active' | 'paused' | 'completed' | 'deleted';
  author: {
    id: number;
    full_name: string;
    avatar_url?: string;
  };
  created_at: string;
  is_suitable: boolean;
  is_completed: boolean;
  user_responses_count?: number; // сколько раз текущий пользователь прошел
}

export interface SurveyCriteria {
  age_min?: number;
  age_max?: number;
  gender?: ('male' | 'female' | 'other')[];
  employment?: ('student' | 'employed' | 'unemployed' | 'self_employed')[];
  income?: ('low' | 'medium' | 'high')[];
  marital_status?: ('single' | 'married' | 'divorced' | 'widowed')[];
  location?: string;
  allow_all?: boolean;
}

export interface CreateSurveyRequest {
  google_account_id: number;
  google_form_url: string;
  category: string;
  theme_color: string;
  criteria?: SurveyCriteria;
  reward?: number; // опционально, если хотим увеличить минимальную награду
  responses_needed?: number;
  max_responses_per_user?: number;
}

export interface SurveyFilters {
  search?: string;
  category?: string;
  min_reward?: number;
  max_reward?: number;
  duration?: 'short' | 'medium' | 'long'; // <5мин, 5-10мин, >10мин
  only_suitable?: boolean;
}

export interface ParticipateResponse {
  message: string;
  google_form_url: string;
}

export interface VerifyParticipationResponse {
  success: boolean;
  message: string;
  reward?: number;
  new_balance?: number;
}

export interface Category {
  id: string;
  name: string;
}
