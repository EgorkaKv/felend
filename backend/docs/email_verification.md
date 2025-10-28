# Email Verification System

## Overview

The email verification system is designed to verify user email addresses during registration. Users must verify their email before they can log in and receive the welcome bonus.

## Flow

```
1. User registers → Receives verification_token
2. User requests verification code → Receives 6-digit code via email
3. User submits code → Account activated + Welcome bonus granted
4. User can now log in
```

## Architecture

### Database Schema

**Table: `email_verifications`**

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to users table |
| verification_token | String(36) | UUID4 token (valid 24 hours) |
| verification_code | String(6) | 6-digit numeric code (valid 15 minutes) |
| code_expires_at | DateTime(TZ) | When the code expires |
| token_expires_at | DateTime(TZ) | When the token expires |
| is_used | Boolean | Whether verification was completed |
| attempts | Integer | Number of failed verification attempts |
| last_code_sent_at | DateTime(TZ) | For rate limiting (60s between requests) |
| created_at | DateTime(TZ) | Record creation time |
| updated_at | DateTime(TZ) | Last update time |

### Components

#### 1. Models (`app/models.py`)
- **EmailVerification**: SQLAlchemy model for email_verifications table

#### 2. Repositories (`app/repositories/email_verification_repository.py`)
- `create_verification()`: Create new verification record with UUID token
- `get_by_token()`: Retrieve verification by token
- `generate_verification_code()`: Generate random 6-digit code
- `increment_attempts()`: Track failed verification attempts
- `mark_as_used()`: Mark verification as completed
- `is_token_valid()`: Check if token hasn't expired
- `is_code_valid()`: Check if code hasn't expired
- `can_request_new_code()`: Rate limiting check (60s cooldown)

#### 3. Services

**`app/services/email_service.py`**
- `send_verification_code()`: Send verification code via SMTP
  - Beautiful HTML email template
  - Fallback to console logging for development
- `mask_email()`: Hide email for security (e.g., `j***n@e***le.com`)

**`app/services/email_verification_service.py`**
- `request_verification_code()`: Generate and send verification code
  - Rate limiting: 60 seconds between requests
  - Returns masked email for security
- `verify_email()`: Verify code and activate account
  - Max 5 attempts before lockout
  - Activates user account
  - Grants welcome bonus (10 points)
  - Returns JWT tokens for immediate login

**`app/services/auth_service.py`**
- Modified `register_user()`:  
  - Creates inactive user (is_active=False)
  - Sets balance to 0 (no welcome bonus yet)
  - Returns tuple: (user, verification_token)

#### 4. API Endpoints (`app/api/v1/auth.py`)

**POST /api/v1/auth/register**
```json
Request:
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "securepass123"
}

Response (201):
{
  "verification_token": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "message": "Registration successful. Please verify your email to activate your account."
}
```

**POST /api/v1/auth/request-verification-code**
```json
Request:
{
  "verification_token": "550e8400-e29b-41d4-a716-446655440000"
}

Response (200):
{
  "success": true,
  "message": "Verification code sent to j***n@e***le.com. Code valid for 15 minutes.",
  "email_masked": "j***n@e***le.com"
}
```

**POST /api/v1/auth/verify-email**
```json
Request:
{
  "verification_token": "550e8400-e29b-41d4-a716-446655440000",
  "code": "123456"
}

Response (200):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "balance": 10,
    "respondent_code": "ABC123",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "Email verified successfully. Welcome to Felend!"
}
```

#### 5. Exceptions (`app/core/exceptions.py`)

| Exception | HTTP Code | Error Code | Description |
|-----------|-----------|------------|-------------|
| VerificationTokenExpiredException | 410 Gone | VERIFY001 | Token expired (>24h) |
| VerificationTokenInvalidException | 404 Not Found | VERIFY002 | Token not found |
| InvalidVerificationCodeException | 400 Bad Request | VERIFY003 | Wrong code entered |
| TooManyAttemptsException | 429 Too Many Requests | VERIFY004 | Max 5 attempts exceeded |
| VerificationRateLimitException | 429 Too Many Requests | VERIFY005 | Must wait 60s between code requests |
| VerificationAlreadyUsedException | 410 Gone | VERIFY006 | Verification already completed |

#### 6. Schemas (`app/schemas.py`)
- **RegisterResponse**: Response for registration with verification_token
- **RequestVerificationCode**: Request schema for code request
- **VerificationCodeResponse**: Response after sending code
- **VerifyEmail**: Request schema for email verification
- **EmailVerifiedResponse**: Response after successful verification (with tokens and user data)

## Security Features

### 1. Token Security
- **UUID4 tokens**: Cryptographically secure random tokens
- **24-hour expiration**: Tokens automatically expire
- **Single-use**: Tokens marked as used after verification

### 2. Code Security
- **6-digit numeric codes**: Easy to type, hard to guess (1 in 1,000,000)
- **15-minute expiration**: Short validity window
- **Max 5 attempts**: Prevents brute force attacks

### 3. Rate Limiting
- **60-second cooldown**: Between code requests
- **Prevents abuse**: Can't spam verification emails

### 4. Email Masking
- **Privacy protection**: Email partially hidden in responses
- **Example**: `john.doe@example.com` → `j***e@e***le.com`

### 5. Account Protection
- **Inactive by default**: New accounts can't log in until verified
- **No welcome bonus**: Until email is verified
- **Clear error messages**: Without revealing sensitive information

## Email Configuration

### SMTP Settings (`.env`)
```
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@felend.com
SMTP_FROM_NAME=Felend

# For Gmail, use App Password:
# https://support.google.com/accounts/answer/185833
```

### Email Template
Beautiful HTML email with:
- Felend branding
- Large, easy-to-read verification code
- Expiration notice (15 minutes)
- Security reminder (don't share code)

### Development Mode
If SMTP is not configured:
- Codes are printed to console
- System still works for testing
- No actual emails sent

## Testing

### Test Coverage
The system includes comprehensive tests (`tests/test_email_verification.py`):

1. **Flow Tests**
   - Registration returns verification token
   - Request verification code
   - Verify with correct code
   - Verify with wrong code
   - Verify with expired code
   - Rate limiting enforcement
   - Max attempts enforcement
   - Login fails before verification
   - Full end-to-end flow

2. **Validation Tests**
   - Token must be valid UUID format
   - Code must be 6 digits

3. **Security Tests**
   - Email masking in responses
   - Cannot reuse verification
   - Token expiration

### Running Tests
```bash
# Run all email verification tests
python -m pytest tests/test_email_verification.py -v

# Run all tests
python -m pytest tests/ -v
```

## Database Migration

Migration file: `alembic/versions/49626bde8086_add_email_verifications_table.py`

Apply migration:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

## Usage Example

### Client-Side Flow (JavaScript)
```javascript
// 1. Register
const registerResponse = await fetch('/api/v1/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    full_name: 'John Doe',
    password: 'securepass123'
  })
});
const { verification_token } = await registerResponse.json();

// 2. Request verification code
const codeResponse = await fetch('/api/v1/auth/request-verification-code', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ verification_token })
});
const { email_masked } = await codeResponse.json();
console.log(`Code sent to ${email_masked}`);

// 3. User enters code from email, verify it
const verifyResponse = await fetch('/api/v1/auth/verify-email', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    verification_token,
    code: '123456' // User input
  })
});
const { access_token, user } = await verifyResponse.json();

// 4. Store tokens and redirect to app
localStorage.setItem('access_token', access_token);
console.log(`Welcome ${user.full_name}! Balance: ${user.balance} points`);
```

## Error Handling

All verification errors return consistent JSON format:
```json
{
  "error": {
    "message": "Invalid verification code. 3 attempts remaining",
    "code": "VERIFY003",
    "type": "InvalidVerificationCodeException",
    "details": {
      "attempts_left": 3
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "path": "/api/v1/auth/verify-email",
    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

## Monitoring & Logging

### Logged Events
- Verification token created
- Verification code sent (with masked email)
- Verification code request blocked (rate limit)
- Verification failed (wrong code)
- Verification successful (email activated)
- Too many attempts (account locked)

### Log Format
```
INFO: Verification code sent to user 1 (j***n@e***le.com)
WARNING: FelendException: VERIFY003 - Invalid verification code. 3 attempts remaining
INFO: User 1 (user@example.com) successfully verified email and activated account
```

## Performance Considerations

1. **Database Indexes**
   - `verification_token` (unique, indexed)
   - `user_id` (foreign key, indexed)

2. **Token Expiration**
   - Tokens expire after 24 hours
   - Codes expire after 15 minutes
   - Consider cleanup job for old records

3. **Email Sending**
   - Async email sending recommended for production
   - Use background tasks (Celery, etc.)
   - Implement retry logic

## Future Enhancements

1. **Resend Code Button**: Allow users to request new code easily
2. **Email Templates**: Multiple languages, custom branding
3. **SMS Verification**: Alternative to email
4. **Account Recovery**: Use verification system for password reset
5. **Two-Factor Authentication**: Extend for 2FA
6. **Analytics**: Track verification success rates
7. **Cleanup Job**: Remove expired verifications

## Troubleshooting

### User didn't receive email
1. Check SMTP configuration
2. Check email isn't in spam
3. Verify email service is working
4. Check console logs for development mode

### Code doesn't work
1. Check if code expired (15 minutes)
2. Check if too many attempts (5 max)
3. Verify correct verification_token used
4. Check for typos in code

### Rate limiting issues
1. User must wait 60 seconds between requests
2. Consider increasing limit for production
3. Add clear UI countdown timer

### Token expired
1. User must register again
2. Consider increasing 24-hour limit
3. Add email notification before expiration
