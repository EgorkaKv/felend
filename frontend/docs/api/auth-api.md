## Authentication

### Table of Contents

- [POST /auth/register](#post-authregister) - Register a new user account
- [POST /auth/login](#post-authlogin) - Authenticate user and receive tokens
- [POST /auth/refresh](#post-authrefresh) - Refresh access token using refresh token
- [POST /auth/request-verification-code](#post-authrequest-verification-code) - Request email verification code
- [POST /auth/verify-email](#post-authverify-email) - Verify email with 6-digit code
- [POST /auth/forgot-password](#post-authforgot-password) - Request password reset
- [POST /auth/reset-password](#post-authreset-password) - Reset password with code
- [POST /auth/google/login](#post-authgooglelogin) - Initiate Google OAuth for registration/login
- [GET /auth/google/callback](#get-authgooglecallback) - Google OAuth callback handler
- [POST /auth/google/exchange-token](#post-authgoogleexchange-token) - Exchange temporary token for JWT

---

### POST /auth/register

Register a new user account. Creates an inactive user that must verify their email before full activation.

**Request:**

```json
{
  "email": "student@example.com",
  "password": "securePassword123",
  "full_name": "John Doe"
}
```

**Response (201 Created):**

```json
{
  "verification_token": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "message": "Registration successful. Please verify your email to activate your account."
}
```

**Error Responses:**

**400 Bad Request - Validation Error:**

```json
{
  "error": {
    "message": "Validation error",
    "code": "VALIDATION001",
    "type": "ValidationError",
    "details": [
      {
        "type": "string_too_short",
        "loc": ["body", "password"],
        "msg": "String should have at least 6 characters",
        "input": "12345"
      }
    ],
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/auth/register"
  }
}
```

**409 Conflict - User Already Exists:**

```json
{
  "error": {
    "message": "User with email student@example.com already exists",
    "code": "AUTH002",
    "type": "UserAlreadyExistsException",
    "details": {
      "email": "student@example.com"
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/auth/register"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Internal server error",
    "code": "SERVER001",
    "type": "InternalServerError",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/auth/register"
  }
}
```

---

### POST /auth/login

Authenticate user and receive access/refresh tokens.

**Request:**

```json
{
  "email": "student@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Error Responses:**

**400 Bad Request - Validation Error:**

```json
{
  "error": {
    "message": "Validation error",
    "code": "VALIDATION001",
    "type": "ValidationError",
    "details": [
      {
        "type": "value_error",
        "loc": ["body", "email"],
        "msg": "value is not a valid email address",
        "input": "notanemail"
      }
    ],
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/auth/login"
  }
}
```

**401 Unauthorized - Invalid Credentials:**

```json
{
  "error": {
    "message": "Invalid email or password",
    "code": "AUTH001",
    "type": "InvalidCredentialsException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/auth/login"
  }
}
```

**401 Unauthorized - Account Not Verified:**

```json
{
  "error": {
    "message": "Email not verified. Please verify your email to login.",
    "code": "AUTH003",
    "type": "EmailNotVerifiedException",
    "details": {
      "email": "student@example.com"
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/auth/login"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Internal server error",
    "code": "SERVER001",
    "type": "InternalServerError",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/auth/login"
  }
}
```

---

### POST /auth/request-verification-code

Request a 6-digit verification code to be sent to the user's email. Can only be requested once per 60 seconds.

**Request:**

```json
{
  "verification_token": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Verification code sent to your email",
  "email_masked": "s*****t@example.com"
}
```

**Error Responses:**

**400 Bad Request - Invalid Token:**

```json
{
  "error": {
    "message": "Invalid verification token format",
    "code": "VALIDATION001",
    "type": "ValidationError",
    "details": [
      {
        "type": "string_pattern_mismatch",
        "loc": ["body", "verification_token"],
        "msg": "String should match pattern",
        "input": "invalid-token"
      }
    ],
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/auth/request-verification-code"
  }
}
```

**404 Not Found - Verification Not Found:**

```json
{
  "error": {
    "message": "Verification token not found",
    "code": "VERIFY001",
    "type": "VerificationNotFoundException",
    "details": {
      "token": "550e8400-e29b-41d4-a716-446655440000"
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/auth/request-verification-code"
  }
}
```

**429 Too Many Requests - Rate Limit:**

```json
{
  "error": {
    "message": "Please wait 60 seconds before requesting a new code",
    "code": "VERIFY002",
    "type": "RateLimitExceededException",
    "details": {
      "retry_after": 45
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/auth/request-verification-code"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Failed to send verification email",
    "code": "EMAIL001",
    "type": "EmailSendException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/auth/request-verification-code"
  }
}
```

---

### POST /auth/verify-email

Verify email address using the 6-digit code. Upon successful verification, activates the account and returns authentication tokens. Maximum 5 attempts allowed.

**Request:**

```json
{
  "verification_token": "550e8400-e29b-41d4-a716-446655440000",
  "code": "123456"
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "student@example.com",
    "full_name": "John Doe",
    "balance": 50,
    "respondent_code": "RESP123456",
    "created_at": "2025-10-21T12:00:00Z"
  },
  "message": "Email verified successfully. Welcome to Felend!"
}
```

**Error Responses:**

**400 Bad Request - Invalid Code:**

```json
{
  "error": {
    "message": "Invalid verification code",
    "code": "VERIFY003",
    "type": "InvalidVerificationCodeException",
    "details": {
      "attempts_remaining": 3
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/auth/verify-email"
  }
}
```

**400 Bad Request - Validation Error:**

```json
{
  "error": {
    "message": "Validation error",
    "code": "VALIDATION001",
    "type": "ValidationError",
    "details": [
      {
        "type": "string_pattern_mismatch",
        "loc": ["body", "code"],
        "msg": "String should match pattern '^\\d{6}$'",
        "input": "12345"
      }
    ],
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/auth/verify-email"
  }
}
```

**404 Not Found - Verification Not Found:**

```json
{
  "error": {
    "message": "Verification token not found",
    "code": "VERIFY001",
    "type": "VerificationNotFoundException",
    "details": {
      "token": "550e8400-e29b-41d4-a716-446655440000"
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/auth/verify-email"
  }
}
```

**410 Gone - Token Expired or Already Used:**

```json
{
  "error": {
    "message": "Verification token has expired or already been used",
    "code": "VERIFY004",
    "type": "VerificationTokenExpiredException",
    "details": {
      "expired_at": "2025-10-21T11:00:00Z"
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/auth/verify-email"
  }
}
```

**429 Too Many Requests - Too Many Attempts:**

```json
{
  "error": {
    "message": "Too many verification attempts. Please request a new code.",
    "code": "VERIFY005",
    "type": "TooManyAttemptsException",
    "details": {
      "max_attempts": 5
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/auth/verify-email"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Internal server error",
    "code": "SERVER001",
    "type": "InternalServerError",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/auth/verify-email"
  }
}
```

---

### POST /auth/refresh

Refresh an expired access token using a valid refresh token.

**Request:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Error Responses:**

**400 Bad Request - Validation Error:**

```json
{
  "error": {
    "message": "Validation error",
    "code": "VALIDATION001",
    "type": "ValidationError",
    "details": [
      {
        "type": "missing",
        "loc": ["body", "refresh_token"],
        "msg": "Field required",
        "input": {}
      }
    ],
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/refresh"
  }
}
```

**401 Unauthorized - Invalid Token:**

```json
{
  "error": {
    "message": "Invalid or expired refresh token",
    "code": "AUTH006",
    "type": "InvalidTokenException",
    "details": null,
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/refresh"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Internal server error",
    "code": "SERVER001",
    "type": "InternalServerError",
    "details": null,
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/refresh"
  }
}
```

---

### POST /auth/forgot-password

Request a password reset code. Sends a 6-digit code to the user's email. Rate limited to 3 requests per hour per user. Code expires in 15 minutes.

**Request:**

```json
{
  "email": "student@example.com"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "If an account with this email exists, a password reset code has been sent",
  "email_masked": "s*****t@example.com"
}
```

**Error Responses:**

**400 Bad Request - Validation Error:**

```json
{
  "error": {
    "message": "Validation error",
    "code": "VALIDATION001",
    "type": "ValidationError",
    "details": [
      {
        "type": "value_error",
        "loc": ["body", "email"],
        "msg": "value is not a valid email address",
        "input": "not-an-email"
      }
    ],
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/forgot-password"
  }
}
```

**429 Too Many Requests - Rate Limit:**

```json
{
  "error": {
    "message": "Too many password reset requests. Please try again later",
    "code": "VERIFY002",
    "type": "RateLimitExceededException",
    "details": {
      "retry_after": 1800
    },
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/forgot-password"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Failed to send password reset email",
    "code": "EMAIL001",
    "type": "EmailSendException",
    "details": null,
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/forgot-password"
  }
}
```

---

### POST /auth/reset-password

Reset password using the 6-digit code from email. Maximum 5 attempts allowed per reset request.

**Request:**

```json
{
  "email": "student@example.com",
  "code": "123456",
  "new_password": "newSecurePassword123"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Password successfully reset",
  "user": {
    "id": 1,
    "email": "student@example.com",
    "full_name": "John Doe"
  }
}
```

**Error Responses:**

**400 Bad Request - Invalid Code:**

```json
{
  "error": {
    "message": "Invalid password reset code",
    "code": "VERIFY003",
    "type": "InvalidVerificationCodeException",
    "details": {
      "attempts_remaining": 3
    },
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/reset-password"
  }
}
```

**400 Bad Request - Validation Error:**

```json
{
  "error": {
    "message": "Validation error",
    "code": "VALIDATION001",
    "type": "ValidationError",
    "details": [
      {
        "type": "string_too_short",
        "loc": ["body", "new_password"],
        "msg": "String should have at least 6 characters",
        "input": "12345"
      }
    ],
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/reset-password"
  }
}
```

**404 Not Found - No Active Reset Request:**

```json
{
  "error": {
    "message": "No active password reset request found",
    "code": "VERIFY001",
    "type": "VerificationNotFoundException",
    "details": {
      "email": "student@example.com"
    },
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/reset-password"
  }
}
```

**410 Gone - Reset Request Expired:**

```json
{
  "error": {
    "message": "Password reset request has expired",
    "code": "VERIFY004",
    "type": "VerificationTokenExpiredException",
    "details": {
      "expired_at": "2025-10-28T11:45:00Z"
    },
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/reset-password"
  }
}
```

**429 Too Many Requests - Too Many Attempts:**

```json
{
  "error": {
    "message": "Too many failed attempts. Please request a new password reset code",
    "code": "VERIFY005",
    "type": "TooManyAttemptsException",
    "details": {
      "max_attempts": 5
    },
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/reset-password"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Internal server error",
    "code": "SERVER001",
    "type": "InternalServerError",
    "details": null,
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/reset-password"
  }
}
```

---

### POST /auth/google/login

Initiate Google OAuth flow for registration/login. Returns a Google authorization URL that the frontend should redirect the user to.

**Request:**

```json
{
  "frontend_redirect_uri": "http://localhost:5173/auth/google/callback"
}
```

**Response (200 OK):**

```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=...&redirect_uri=...&scope=openid+email+profile&state=...",
  "message": "Redirect to Google for authentication"
}
```

**Important:** Frontend must redirect user to `authorization_url` using `window.location.href`, not fetch/axios (to avoid CORS issues).

**Error Responses:**

**400 Bad Request - Validation Error:**

```json
{
  "error": {
    "message": "Validation error",
    "code": "VALIDATION001",
    "type": "ValidationError",
    "details": [
      {
        "type": "url_parsing",
        "loc": ["body", "frontend_redirect_uri"],
        "msg": "Invalid URL format",
        "input": "not-a-url"
      }
    ],
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/google/login"
  }
}
```

**422 Unprocessable Entity - Invalid Origin:**

```json
{
  "error": {
    "message": "Frontend origin http://malicious.com is not allowed",
    "code": "OAUTH001",
    "type": "InvalidFrontendOriginException",
    "details": {
      "origin": "http://malicious.com",
      "allowed_origins": ["http://localhost:5173", "http://localhost:3000"]
    },
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/google/login"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Internal server error",
    "code": "SERVER001",
    "type": "InternalServerError",
    "details": null,
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/google/login"
  }
}
```

---

### GET /auth/google/callback

Google OAuth callback endpoint. Handles the authorization code from Google, creates or authenticates the user, and redirects to the frontend with a temporary token.

**Query Parameters:**

- `code` (required): Authorization code from Google
- `state` (required): JWT state token containing frontend_redirect_uri

**Response (302 Found):**

Redirects to: `{frontend_redirect_uri}?token={temporary_token}`

Example: `http://localhost:5173/auth/google/callback?token=550e8400-e29b-41d4-a716-446655440000`

**Error Responses:**

If an error occurs, redirects to frontend with error parameters:

`{frontend_redirect_uri}?error={error_code}&message={error_message}`

**400 Bad Request - Invalid State:**

Redirects to: `{frontend_redirect_uri}?error=OAUTH001&message=Invalid+state+token`

**500 Internal Server Error:**

Redirects to: `{frontend_redirect_uri}?error=SERVER001&message=Internal+server+error`

---

### POST /auth/google/exchange-token

Exchange a temporary one-time token for JWT access and refresh tokens. The temporary token is valid for 5 minutes and can only be used once.

**Request:**

```json
{
  "token": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "user@gmail.com",
    "full_name": "John Doe",
    "balance": 50,
    "respondent_code": "RESP123456",
    "created_at": "2025-10-28T12:00:00Z"
  }
}
```

**Error Responses:**

**400 Bad Request - Validation Error:**

```json
{
  "error": {
    "message": "Validation error",
    "code": "VALIDATION001",
    "type": "ValidationError",
    "details": [
      {
        "type": "string_type",
        "loc": ["body", "token"],
        "msg": "Input should be a valid string",
        "input": null
      }
    ],
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/google/exchange-token"
  }
}
```

**401 Unauthorized - Token Expired:**

```json
{
  "error": {
    "message": "Temporary token has expired",
    "code": "OAUTH003",
    "type": "TemporaryTokenExpiredException",
    "details": {
      "token": "550e8400-e29b-41d4-a716-446655440000",
      "expired_at": "2025-10-28T11:55:00Z"
    },
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/google/exchange-token"
  }
}
```

**404 Not Found - Token Not Found:**

```json
{
  "error": {
    "message": "Temporary token not found or already used",
    "code": "OAUTH002",
    "type": "TemporaryTokenNotFoundException",
    "details": {
      "token": "550e8400-e29b-41d4-a716-446655440000"
    },
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/google/exchange-token"
  }
}
```

**410 Gone - Token Already Used:**

```json
{
  "error": {
    "message": "Temporary token has already been used",
    "code": "OAUTH004",
    "type": "TemporaryTokenAlreadyUsedException",
    "details": {
      "token": "550e8400-e29b-41d4-a716-446655440000",
      "used_at": "2025-10-28T11:58:00Z"
    },
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/google/exchange-token"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Internal server error",
    "code": "SERVER001",
    "type": "InternalServerError",
    "details": null,
    "timestamp": "2025-10-28T12:00:00Z",
    "path": "/api/v1/auth/google/exchange-token"
  }
}
```