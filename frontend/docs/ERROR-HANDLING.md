# Error Handling Guide

Руководство по обработке ошибок в Felend Frontend.

## 📋 Содержание

- [Структура ошибок API](#структура-ошибок-api)
- [Использование getErrorMessage()](#использование-geterrormessage)
- [Примеры обработки ошибок](#примеры-обработки-ошибок)
- [Коды ошибок](#коды-ошибок)
- [Best Practices](#best-practices)

---

## Структура ошибок API

Все ошибки от бэкенда приходят в стандартном формате (согласно `/docs/api/README.md`):

```typescript
{
  "error": {
    "message": "User with this email already exists",  // Human-readable message
    "code": "AUTH002",                                  // Error code
    "type": "UserAlreadyExistsException",              // Exception type
    "details": {},                                      // Additional context (optional)
    "timestamp": "2025-10-27T10:30:00Z",               // ISO 8601 timestamp (optional)
    "path": "/api/v1/auth/register"                    // API endpoint (optional)
  }
}
```

### TypeScript Types

```typescript
// src/types/api.ts
export interface ApiError {
  message: string;
  code: string;
  type: string;
  details?: Record<string, unknown>;
  timestamp?: string;
  path?: string;
}

export interface ApiErrorResponse {
  error: ApiError;
  detail?: string;  // Legacy format fallback
}
```

---

## Использование getErrorMessage()

### Импорт

```typescript
import { getErrorMessage, logError } from '@/utils/errorHandler';
```

### Базовое использование

```typescript
try {
  await someApiCall();
} catch (error) {
  const errorMessage = getErrorMessage(error);
  dispatch(showSnackbar({ message: errorMessage, severity: 'error' }));
}
```

### С логированием (dev mode)

```typescript
try {
  await someApiCall();
} catch (error) {
  const errorMessage = getErrorMessage(error);
  logError('ComponentName', error);  // Logs in dev mode only
  dispatch(showSnackbar({ message: errorMessage, severity: 'error' }));
}
```

---

## Примеры обработки ошибок

### Authentication (useAuth hook)

```typescript
// src/hooks/useAuth.ts
import { getErrorMessage, logError } from '@/utils/errorHandler';

const register = async (data: RegisterRequest) => {
  try {
    const response = await authApi.register(data);
    // Success handling...
  } catch (error) {
    const errorMessage = getErrorMessage(error);
    logError('Register', error);
    dispatch(showSnackbar({ message: errorMessage, severity: 'error' }));
    throw error;
  }
};
```

**Возможные ошибки:**
- `AUTH002`: "User with this email already exists"
- `VALIDATION001`: "Request validation failed"
- Network error: "Network error. Please check your connection"

### Survey Creation (AddSurveyPage)

```typescript
// src/pages/AddSurveyPage.tsx
import { getErrorMessage } from '@/utils/errorHandler';

const onSubmit = async (data: SurveyFormData) => {
  try {
    await createSurvey(requestData);
    dispatch(showSnackbar({ message: 'Survey created!', severity: 'success' }));
  } catch (error) {
    const errorMessage = getErrorMessage(error);
    dispatch(showSnackbar({ message: errorMessage, severity: 'error' }));
  }
};
```

**Возможные ошибки:**
- `SURVEY001`: "Not enough balance"
- `FORM001`: "Invalid Google Form URL"
- `FORM002`: "No access to form"
- `GOOGLE001`: "Google account not found"

### Profile Update

```typescript
// src/pages/ProfilePage.tsx
import { getErrorMessage } from '@/utils/errorHandler';

const onSubmit = async (data: ProfileFormData) => {
  try {
    await updateUser(updateData);
    dispatch(showSnackbar({ message: 'Profile updated', severity: 'success' }));
  } catch (error) {
    const errorMessage = getErrorMessage(error);
    dispatch(showSnackbar({ message: errorMessage, severity: 'error' }));
  }
};
```

**Возможные ошибки:**
- `AUTH004`: "User not authenticated"
- `VALIDATION001`: "Request validation failed"

---

## Коды ошибок

### Authentication (AUTH)

| Code | Type | Message |
|------|------|---------|
| AUTH001 | InvalidCredentialsException | Invalid email or password |
| AUTH002 | UserAlreadyExistsException | User with this email already exists |
| AUTH003 | EmailNotVerifiedException | Email not verified |
| AUTH004 | NotAuthenticatedException | User not authenticated |
| AUTH005 | AccountInactiveException | User account is not active |

### Verification (VERIFY)

| Code | Type | Message |
|------|------|---------|
| VERIFY001 | VerificationNotFoundException | Verification token not found |
| VERIFY002 | RateLimitExceededException | Too many requests, wait before retry |
| VERIFY003 | InvalidVerificationCodeException | Invalid verification code |
| VERIFY004 | VerificationTokenExpiredException | Verification token expired |
| VERIFY005 | TooManyAttemptsException | Too many verification attempts |

### Surveys (SURVEY)

| Code | Type | Message |
|------|------|---------|
| SURVEY001 | InsufficientBalanceException | Not enough balance |
| SURVEY002 | SurveyCreationException | Failed to create survey |
| SURVEY003 | MaxResponsesReachedException | Maximum responses reached |
| SURVEY004 | CannotParticipateSelfException | Cannot participate in own survey |
| SURVEY005 | SurveyNotFoundException | Survey not found |

### Google Forms (FORM, GOOGLE)

| Code | Type | Message |
|------|------|---------|
| FORM001 | InvalidFormUrlException | Invalid Google Form URL |
| FORM002 | FormAccessDeniedException | No access to form |
| GOOGLE001 | GoogleAccountNotFoundException | Google account not found |

### Server (SERVER)

| Code | Type | Message |
|------|------|---------|
| SERVER001 | InternalServerError | Internal server error |

### Validation (VALIDATION)

| Code | Type | Message |
|------|------|---------|
| VALIDATION001 | ValidationError | Request validation failed |

---

## Best Practices

### ✅ DO

1. **Всегда используйте `getErrorMessage()`:**
   ```typescript
   const errorMessage = getErrorMessage(error);
   ```

2. **Показывайте детальные ошибки пользователю:**
   ```typescript
   dispatch(showSnackbar({ message: errorMessage, severity: 'error' }));
   ```

3. **Логируйте ошибки в dev режиме:**
   ```typescript
   logError('ComponentName', error);
   ```

4. **Обрабатывайте специфичные кейсы если нужно:**
   ```typescript
   if (axios.isAxiosError(error) && error.response?.status === 401) {
     // Redirect to login
   }
   ```

### ❌ DON'T

1. **Не используйте generic сообщения:**
   ```typescript
   // ❌ BAD
   catch (error) {
     dispatch(showSnackbar({ message: 'Ошибка', severity: 'error' }));
   }
   
   // ✅ GOOD
   catch (error) {
     const errorMessage = getErrorMessage(error);
     dispatch(showSnackbar({ message: errorMessage, severity: 'error' }));
   }
   ```

2. **Не игнорируйте детали ошибки:**
   ```typescript
   // ❌ BAD
   catch (error) {
     console.log('Error occurred');
   }
   
   // ✅ GOOD
   catch (error) {
     logError('ComponentName', error);
   }
   ```

3. **Не дублируйте логику извлечения ошибок:**
   ```typescript
   // ❌ BAD
   catch (error) {
     const message = error?.response?.data?.error?.message || 'Error';
   }
   
   // ✅ GOOD
   catch (error) {
     const errorMessage = getErrorMessage(error);
   }
   ```

---

## Error Flow Diagram

```
API Call
   ↓
Error occurs
   ↓
axios interceptor (src/api/client.ts)
   ↓
getErrorMessage() (src/utils/errorHandler.ts)
   ↓
Extracts: error.message → detail → network → status → fallback
   ↓
Return human-readable message
   ↓
Show in Snackbar
```

---

## Network Errors

### Типы network ошибок:

1. **ERR_NETWORK** - No internet connection
   - Message: "Network error. Please check your connection"

2. **401 Unauthorized** - Not authenticated
   - Message: "User not authenticated"
   - Action: Redirect to login

3. **403 Forbidden** - No access
   - Message: "Access forbidden"

4. **404 Not Found** - Resource not found
   - Message: "Resource not found"

5. **500 Internal Server Error** - Server error
   - Message: "Internal server error"

---

## Testing Error Handling

### Manual Testing

1. **Test with backend running:**
   ```bash
   npm run dev
   ```

2. **Test specific errors:**
   - Register with existing email → AUTH002
   - Login with wrong password → AUTH001
   - Create survey without balance → SURVEY001
   - Invalid verification code → VERIFY003

3. **Test network errors:**
   - Disconnect internet → ERR_NETWORK
   - Stop backend → Connection refused

### Console Logs (Dev Mode)

```javascript
// Success
[Register] Register API success { verification_token: '***' }

// Error
[REGISTER ERROR] {
  message: "User with this email already exists",
  status: 400,
  code: "AUTH002",
  data: { error: {...} }
}
```

---

## Migration Checklist

При добавлении нового API endpoint:

- [ ] Используйте `getErrorMessage()` в catch блоке
- [ ] Добавьте `logError()` для dev логирования (опционально)
- [ ] Документируйте возможные коды ошибок
- [ ] Тестируйте все error cases
- [ ] Обновите эту документацию если нужно

---

## Support

Если возникли вопросы:
1. Проверьте `/docs/api/README.md` для списка всех кодов ошибок
2. Посмотрите примеры в `useAuth.ts`, `AddSurveyPage.tsx`, `ProfilePage.tsx`
3. Используйте DevTools (F12) для просмотра логов в dev режиме

---

**Last Updated:** October 27, 2025  
**Version:** 1.0.0
