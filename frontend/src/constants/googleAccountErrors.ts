// Маппинг кодов ошибок подключения Google аккаунта на русский язык

export const GOOGLE_ACCOUNT_ERROR_MESSAGES: Record<string, string> = {
  invalid_state: 'Недействительный или истекший параметр состояния',
  user_not_found: 'Пользователь не найден',
  account_already_connected: 'Этот Google аккаунт уже подключен к вашей учетной записи',
  account_connected_to_another_user: 'Этот Google аккаунт уже подключен к другому пользователю',
  google_api_error: 'Не удалось получить данные от Google. Попробуйте позже',
  internal_error: 'Произошла непредвиденная ошибка. Попробуйте позже',
};

/**
 * Получить русское сообщение об ошибке по error_code
 * @param errorCode - Код ошибки от бэкенда
 * @param fallbackMessage - Сообщение по умолчанию (если код не найден)
 * @returns Локализованное сообщение об ошибке
 */
export const getGoogleAccountErrorMessage = (
  errorCode: string,
  fallbackMessage?: string
): string => {
  return GOOGLE_ACCOUNT_ERROR_MESSAGES[errorCode] || fallbackMessage || 'Произошла ошибка при подключении Google аккаунта';
};
