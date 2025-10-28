# API документация 
Ко всем ендпоинтам префикс /api/v1

## Error Response Format

В описаниях ендпоинтов используется короткий формат ошибки где описаны только поля
- message
- code
- type
Но ошибка всегда приходит вот в таком стандартном формате:

```json
{
  "error": {
    "message": "Human-readable error message",
    "code": "ERROR_CODE",
    "type": "ExceptionType",
    "details": {
      "additional": "context-specific information"
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/endpoint"
  }
}
```

### Common Error Codes

| Code | Type | Description |
|------|------|-------------|
| AUTH001 | InvalidCredentialsException | Invalid email or password |
| AUTH002 | UserAlreadyExistsException | User with this email already exists |
| AUTH003 | EmailNotVerifiedException | Email not verified |
| AUTH004 | NotAuthenticatedException | User not authenticated |
| AUTH005 | AccountInactiveException | User account is not active |
| VALIDATION001 | ValidationError | Request validation failed |
| VERIFY001 | VerificationNotFoundException | Verification token not found |
| VERIFY002 | RateLimitExceededException | Too many requests, wait before retry |
| VERIFY003 | InvalidVerificationCodeException | Invalid verification code |
| VERIFY004 | VerificationTokenExpiredException | Verification token expired |
| VERIFY005 | TooManyAttemptsException | Too many verification attempts |
| SURVEY001 | InsufficientBalanceException | Not enough balance |
| SURVEY002 | SurveyCreationException | Failed to create survey |
| SURVEY003 | MaxResponsesReachedException | Maximum responses reached |
| SURVEY004 | CannotParticipateSelfException | Cannot participate in own survey |
| SURVEY005 | SurveyNotFoundException | Survey not found |
| GOOGLE001 | GoogleAccountNotFoundException | Google account not found |
| FORM001 | InvalidFormUrlException | Invalid Google Form URL |
| FORM002 | FormAccessDeniedException | No access to form |
| SERVER001 | InternalServerError | Internal server error |

# Auth enpoints
located in ./auth-api.md 
- POST /auth/register 
- POST /auth/login
- POST /auth/request-verification-code
- POST /auth/verify-email

# Surveys enpoints
located in ./surveys-api.md
- GET /surveys - получить все активные опросы
- GET /surveys/my/ - получить мои опросы
- POST /surveys/my/ - создать новый опрос
- POST /surveys/validate - проверить ссылку на гугл форму
- POST /surveys/{survey_id}/participate - принять участие в опросе
- POST /surveys/{survey_id}/verify - проверить что опрос заполнен

# Users endpoints
located in ./surveys-api.md
- GET users/me
- PUT users/me
- GET user/me/transactions

# Google-accounts endpoints
located in ./google-accounts-api.md
- GET /google-accounts - получить список гугл аккаунтов