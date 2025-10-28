## Error Response Format

All error responses follow a standardized format:

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

| Code          | Type                               | Description                          |
| ------------- | ---------------------------------- | ------------------------------------ |
| AUTH001       | InvalidCredentialsException        | Invalid email or password            |
| AUTH002       | UserAlreadyExistsException         | User with this email already exists  |
| AUTH003       | EmailNotVerifiedException          | Email not verified                   |
| AUTH004       | NotAuthenticatedException          | User not authenticated               |
| AUTH005       | AccountInactiveException           | User account is not active           |
| AUTH006       | InvalidTokenException              | Invalid or expired token             |
| VALIDATION001 | ValidationError                    | Request validation failed            |
| VERIFY001     | VerificationNotFoundException      | Verification token not found         |
| VERIFY002     | RateLimitExceededException         | Too many requests, wait before retry |
| VERIFY003     | InvalidVerificationCodeException   | Invalid verification code            |
| VERIFY004     | VerificationTokenExpiredException  | Verification token expired           |
| VERIFY005     | TooManyAttemptsException           | Too many verification attempts       |
| OAUTH001      | InvalidFrontendOriginException     | Frontend origin not allowed          |
| OAUTH002      | TemporaryTokenNotFoundException    | Temporary token not found/used       |
| OAUTH003      | TemporaryTokenExpiredException     | Temporary token expired              |
| OAUTH004      | TemporaryTokenAlreadyUsedException | Temporary token already used         |
| SURVEY001     | InsufficientBalanceException       | Not enough balance                   |
| SURVEY002     | SurveyCreationException            | Failed to create survey              |
| SURVEY003     | MaxResponsesReachedException       | Maximum responses reached            |
| SURVEY004     | CannotParticipateSelfException     | Cannot participate in own survey     |
| SURVEY005     | SurveyNotFoundException            | Survey not found                     |
| SURVEY006     | ParticipationException             | Failed to start participation        |
| SURVEY007     | NoActiveParticipationException     | No active participation found        |
| SURVEY008     | AlreadyVerifiedException           | Response already verified            |
| SURVEY009     | VerificationFailedException        | Survey completion not verified       |
| SURVEY010     | VerificationException              | Failed to verify completion          |
| GOOGLE001     | GoogleAccountNotFoundException     | Google account not found             |
| GOOGLE002     | GoogleAccountRetrievalException    | Error retrieving Google accounts     |
| GOOGLE003     | GoogleAPIException                 | Google API error                     |
| FORM001       | InvalidFormUrlException            | Invalid Google Form URL              |
| FORM002       | FormAccessDeniedException          | No access to form                    |
| FORM003       | FormValidationException            | Failed to validate form              |
| USER001       | ProfileUpdateException             | Failed to update profile             |
| USER002       | TransactionRetrievalException      | Failed to retrieve transactions      |
| EMAIL001      | EmailSendException                 | Failed to send email                 |
| SERVER001     | InternalServerError                | Internal server error                |
