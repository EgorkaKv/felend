// Типы для транзакций

export interface Transaction {
  id: number;
  type: 'earned' | 'spent';
  amount: number;
  description: string;
  survey_id?: number;
  survey_title?: string;
  balance_after: number;
  created_at: string;
}

export interface TransactionFilters {
  type?: 'earned' | 'spent' | 'all';
}
