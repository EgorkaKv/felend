# Felend API Documentation

This documentation provides detailed information about the Felend API endpoints for frontend development.

## Table of Contents

- [Authentication](#authentication)
  - [POST /auth/register](#post-authregister)
  - [POST /auth/login](#post-authlogin)
  - [POST /auth/request-verification-code](#post-authrequest-verification-code)
  - [POST /auth/verify-email](#post-authverify-email)
- [Surveys](#surveys)
  - [GET /surveys](#get-surveys)
  - [GET /surveys/my/](#get-surveysmy)
  - [POST /surveys/validate](#post-surveysvalidate)
  - [POST /surveys/my/](#post-surveysmy)
  - [POST /surveys/{survey_id}/participate](#post-surveyssurvey_idparticipate)
  - [POST /surveys/{survey_id}/verify](#post-surveyssurvey_idverify)
- [Users](#users)
  - [GET /users/me](#get-usersme)
  - [PUT /users/me](#put-usersme)
  - [GET /users/me/transactions](#get-usersmetransactions)
- [Google Accounts](#google-accounts)
  - [GET /google-accounts](#get-google-accounts)

---

## Authentication

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

## Surveys

### GET /surveys

Get the feed of active surveys available for participation. Supports pagination and optional search.

**Query Parameters:**

- `skip` (integer, optional, default: 0): Number of items to skip
- `limit` (integer, optional, default: 50, max: 100): Number of items to return
- `search` (string, optional): Search query (minimum 1 character)

**Request:**

```
GET /api/v1/surveys?skip=0&limit=10&search=student
```

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "title": "Student Nutrition Survey",
    "description": "Help us understand student eating habits",
    "author_name": "Research Team",
    "reward_per_response": 15,
    "total_responses": 42,
    "responses_needed": 100,
    "questions_count": 12,
    "can_participate": true,
    "my_responses_count": 0
  },
  {
    "id": 2,
    "title": "Campus Life Feedback",
    "description": "Share your campus experience",
    "author_name": "John Doe",
    "reward_per_response": 10,
    "total_responses": 78,
    "responses_needed": 150,
    "questions_count": 8,
    "can_participate": false,
    "my_responses_count": 1
  }
]
```

**Error Responses:**

**400 Bad Request - Invalid Parameters:**

```json
{
  "error": {
    "message": "Validation error",
    "code": "VALIDATION001",
    "type": "ValidationError",
    "details": [
      {
        "type": "greater_than_equal",
        "loc": ["query", "skip"],
        "msg": "Input should be greater than or equal to 0",
        "input": "-1"
      }
    ],
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys"
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
    "path": "/api/v1/surveys"
  }
}
```

---

### GET /surveys/my/

Get list of surveys created by the authenticated user. Requires authentication.

**Query Parameters:**

- `skip` (integer, optional, default: 0): Number of items to skip
- `limit` (integer, optional, default: 50, max: 100): Number of items to return
- `google_account_id` (integer, optional): Filter by specific Google account ID

**Request:**

```
GET /api/v1/surveys/my/?skip=0&limit=10
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**

```json
[
  {
    "id": 5,
    "title": "My Research Survey",
    "description": "Understanding student behavior",
    "status": "active",
    "google_form_url": "https://docs.google.com/forms/d/e/1FAIpQLSc...",
    "reward_per_response": 20,
    "responses_needed": 50,
    "max_responses_per_user": 1,
    "total_responses": 23,
    "total_spent": 460,
    "questions_count": 15,
    "collects_emails": true,
    "created_at": "2025-10-20T10:30:00Z"
  }
]
```

**Error Responses:**

**401 Unauthorized - Not Authenticated:**

```json
{
  "error": {
    "message": "Not authenticated",
    "code": "AUTH004",
    "type": "NotAuthenticatedException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/my/"
  }
}
```

**403 Forbidden - Account Inactive:**

```json
{
  "error": {
    "message": "Account is not active",
    "code": "AUTH005",
    "type": "AccountInactiveException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/my/"
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
    "path": "/api/v1/surveys/my/"
  }
}
```

---

### POST /surveys/validate

Validate Google Form URL and check if the authenticated user has access to it with their Google account.

**Request:**

```json
{
  "google_account_id": 1,
  "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSc.../viewform"
}
```

**Response (200 OK):**

```json
{
  "form_id": "1FAIpQLSc...",
  "title": "Student Nutrition Survey",
  "description": "This survey aims to understand eating habits of university students",
  "collect_emails": true,
  "questions_count": 12,
  "estimated_time_minutes": 5,
  "min_rewards": 10
}
```

**Error Responses:**

**400 Bad Request - Invalid URL:**

```json
{
  "error": {
    "message": "Invalid Google Form URL format",
    "code": "FORM001",
    "type": "InvalidFormUrlException",
    "details": {
      "url": "https://invalid-url.com"
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/validate"
  }
}
```

**401 Unauthorized - Not Authenticated:**

```json
{
  "error": {
    "message": "Not authenticated",
    "code": "AUTH004",
    "type": "NotAuthenticatedException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/validate"
  }
}
```

**403 Forbidden - No Access to Form:**

```json
{
  "error": {
    "message": "No access to this form with the selected Google account",
    "code": "FORM002",
    "type": "FormAccessDeniedException",
    "details": {
      "google_account_id": 1,
      "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSc..."
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/validate"
  }
}
```

**404 Not Found - Google Account Not Found:**

```json
{
  "error": {
    "message": "Google account not found or not accessible",
    "code": "GOOGLE001",
    "type": "GoogleAccountNotFoundException",
    "details": {
      "google_account_id": 99
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/validate"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Failed to validate Google Form",
    "code": "FORM003",
    "type": "FormValidationException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/validate"
  }
}
```

---

### POST /surveys/my/

Create a new survey. Requires authentication and sufficient balance.

**Request:**

```json
{
  "google_account_id": 1,
  "google_form_url": "https://docs.google.com/forms/d/e/1FAIpQLSc.../viewform",
  "reward_per_response": 15,
  "responses_needed": 100,
  "max_responses_per_user": 1
}
```

**Response (201 Created):**

```json
{
  "id": 10,
  "title": "Student Nutrition Survey",
  "description": "Help us understand student eating habits",
  "status": "active",
  "google_form_url": "https://docs.google.com/forms/d/e/1FAIpQLSc.../viewform",
  "reward_per_response": 15,
  "responses_needed": 100,
  "max_responses_per_user": 1,
  "total_responses": 0,
  "total_spent": 0,
  "questions_count": 12,
  "collects_emails": true,
  "created_at": "2025-10-21T12:00:00Z"
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
        "type": "greater_than_equal",
        "loc": ["body", "reward_per_response"],
        "msg": "Input should be greater than or equal to 1",
        "input": 0
      }
    ],
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/my/"
  }
}
```

**401 Unauthorized - Not Authenticated:**

```json
{
  "error": {
    "message": "Not authenticated",
    "code": "AUTH004",
    "type": "NotAuthenticatedException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/my/"
  }
}
```

**403 Forbidden - Insufficient Balance:**

```json
{
  "error": {
    "message": "Insufficient balance to create survey",
    "code": "SURVEY001",
    "type": "InsufficientBalanceException",
    "details": {
      "required": 1500,
      "available": 500
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/my/"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Failed to create survey",
    "code": "SURVEY002",
    "type": "SurveyCreationException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/my/"
  }
}
```

---

### POST /surveys/{survey_id}/participate

Start participation in a survey. Returns the Google Form URL and instructions.

**Request:**

```
POST /api/v1/surveys/5/participate
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**

```json
{
  "google_form_url": "https://docs.google.com/forms/d/e/1FAIpQLSc.../viewform?entry.123456=RESP789012",
  "respondent_code": "RESP789012",
  "instructions": "Please complete the survey and return here to verify completion and receive your reward."
}
```

**Error Responses:**

**400 Bad Request - Already Participated:**

```json
{
  "error": {
    "message": "You have already reached the maximum number of responses for this survey",
    "code": "SURVEY003",
    "type": "MaxResponsesReachedException",
    "details": {
      "survey_id": 5,
      "max_allowed": 1,
      "current_count": 1
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/5/participate"
  }
}
```

**401 Unauthorized - Not Authenticated:**

```json
{
  "error": {
    "message": "Not authenticated",
    "code": "AUTH004",
    "type": "NotAuthenticatedException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/5/participate"
  }
}
```

**403 Forbidden - Cannot Participate in Own Survey:**

```json
{
  "error": {
    "message": "You cannot participate in your own survey",
    "code": "SURVEY004",
    "type": "CannotParticipateSelfException",
    "details": {
      "survey_id": 5
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/5/participate"
  }
}
```

**404 Not Found - Survey Not Found:**

```json
{
  "error": {
    "message": "Survey not found",
    "code": "SURVEY005",
    "type": "SurveyNotFoundException",
    "details": {
      "survey_id": 999
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/999/participate"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Failed to start survey participation",
    "code": "SURVEY006",
    "type": "ParticipationException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/5/participate"
  }
}
```

---

### POST /surveys/{survey_id}/verify

Verify survey completion and award points to the user.

**Request:**

```
POST /api/v1/surveys/5/verify
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**

```json
{
  "verified": true,
  "reward_earned": 15,
  "new_balance": 515,
  "message": "Survey completed successfully! You earned 15 points."
}
```

**Error Responses:**

**400 Bad Request - No Active Participation:**

```json
{
  "error": {
    "message": "No active participation found for this survey",
    "code": "SURVEY007",
    "type": "NoActiveParticipationException",
    "details": {
      "survey_id": 5
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/5/verify"
  }
}
```

**400 Bad Request - Already Verified:**

```json
{
  "error": {
    "message": "This survey response has already been verified",
    "code": "SURVEY008",
    "type": "AlreadyVerifiedException",
    "details": {
      "survey_id": 5
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/5/verify"
  }
}
```

**401 Unauthorized - Not Authenticated:**

```json
{
  "error": {
    "message": "Not authenticated",
    "code": "AUTH004",
    "type": "NotAuthenticatedException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/5/verify"
  }
}
```

**403 Forbidden - Verification Failed:**

```json
{
  "error": {
    "message": "Survey completion could not be verified. Please ensure you submitted the form.",
    "code": "SURVEY009",
    "type": "VerificationFailedException",
    "details": {
      "survey_id": 5
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/5/verify"
  }
}
```

**404 Not Found - Survey Not Found:**

```json
{
  "error": {
    "message": "Survey not found",
    "code": "SURVEY005",
    "type": "SurveyNotFoundException",
    "details": {
      "survey_id": 999
    },
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/999/verify"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Failed to verify survey completion",
    "code": "SURVEY010",
    "type": "VerificationException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/surveys/5/verify"
  }
}
```

---

## Users

### GET /users/me

Get the current authenticated user's profile information.

**Request:**

```
GET /api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**

```json
{
  "id": 1,
  "email": "student@example.com",
  "full_name": "John Doe",
  "balance": 500,
  "respondent_code": "RESP123456",
  "created_at": "2025-10-15T10:30:00Z"
}
```

**Error Responses:**

**401 Unauthorized - Not Authenticated:**

```json
{
  "error": {
    "message": "Not authenticated",
    "code": "AUTH004",
    "type": "NotAuthenticatedException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/users/me"
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
    "path": "/api/v1/users/me"
  }
}
```

---

### PUT /users/me

Update the current authenticated user's profile information.

**Request:**

```json
{
  "full_name": "John Michael Doe"
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "email": "student@example.com",
  "full_name": "John Michael Doe",
  "balance": 500,
  "respondent_code": "RESP123456",
  "created_at": "2025-10-15T10:30:00Z"
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
        "loc": ["body", "full_name"],
        "msg": "String should have at least 1 character",
        "input": ""
      }
    ],
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/users/me"
  }
}
```

**401 Unauthorized - Not Authenticated:**

```json
{
  "error": {
    "message": "Not authenticated",
    "code": "AUTH004",
    "type": "NotAuthenticatedException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/users/me"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Failed to update user profile",
    "code": "USER001",
    "type": "ProfileUpdateException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/users/me"
  }
}
```

---

### GET /users/me/transactions

Get the transaction history for the current authenticated user. Supports pagination.

**Query Parameters:**

- `skip` (integer, optional, default: 0): Number of items to skip
- `limit` (integer, optional, default: 50): Number of items to return

**Request:**

```
GET /api/v1/users/me/transactions?skip=0&limit=10
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "transaction_type": "reward",
    "amount": 15,
    "balance_after": 515,
    "description": "Reward for completing survey: Student Nutrition Survey",
    "created_at": "2025-10-21T11:30:00Z",
    "related_survey": {
      "id": 5,
      "title": "Student Nutrition Survey"
    }
  },
  {
    "id": 2,
    "transaction_type": "expense",
    "amount": -20,
    "balance_after": 500,
    "description": "Payment for survey response",
    "created_at": "2025-10-21T10:15:00Z",
    "related_survey": {
      "id": 10,
      "title": "My Research Survey"
    }
  },
  {
    "id": 3,
    "transaction_type": "bonus",
    "amount": 50,
    "balance_after": 520,
    "description": "Welcome bonus",
    "created_at": "2025-10-15T10:30:00Z",
    "related_survey": null
  }
]
```

**Error Responses:**

**400 Bad Request - Invalid Parameters:**

```json
{
  "error": {
    "message": "Validation error",
    "code": "VALIDATION001",
    "type": "ValidationError",
    "details": [
      {
        "type": "greater_than_equal",
        "loc": ["query", "skip"],
        "msg": "Input should be greater than or equal to 0",
        "input": "-1"
      }
    ],
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/users/me/transactions"
  }
}
```

**401 Unauthorized - Not Authenticated:**

```json
{
  "error": {
    "message": "Not authenticated",
    "code": "AUTH004",
    "type": "NotAuthenticatedException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/users/me/transactions"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Failed to retrieve transactions",
    "code": "USER002",
    "type": "TransactionRetrievalException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/users/me/transactions"
  }
}
```

---

## Google Accounts

### GET /google-accounts

Get list of all Google accounts linked to the current authenticated user.

**Request:**

```
GET /api/v1/google-accounts
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**

```json
{
  "google_accounts": [
    {
      "id": 1,
      "email": "student@gmail.com",
      "name": "John Doe",
      "is_primary": true,
      "is_active": true,
      "created_at": "2025-10-15T10:30:00Z"
    },
    {
      "id": 2,
      "email": "research.account@gmail.com",
      "name": "John Research",
      "is_primary": false,
      "is_active": true,
      "created_at": "2025-10-18T14:20:00Z"
    }
  ],
  "total_accounts": 2
}
```

**Error Responses:**

**401 Unauthorized - Not Authenticated:**

```json
{
  "error": {
    "message": "Not authenticated",
    "code": "AUTH004",
    "type": "NotAuthenticatedException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/google-accounts"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Error retrieving Google accounts",
    "code": "GOOGLE002",
    "type": "GoogleAccountRetrievalException",
    "details": null,
    "timestamp": "2025-10-21T12:00:00Z",
    "path": "/api/v1/google-accounts"
  }
}
```

---

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

| Code          | Type                              | Description                          |
| ------------- | --------------------------------- | ------------------------------------ |
| AUTH001       | InvalidCredentialsException       | Invalid email or password            |
| AUTH002       | UserAlreadyExistsException        | User with this email already exists  |
| AUTH003       | EmailNotVerifiedException         | Email not verified                   |
| AUTH004       | NotAuthenticatedException         | User not authenticated               |
| AUTH005       | AccountInactiveException          | User account is not active           |
| VALIDATION001 | ValidationError                   | Request validation failed            |
| VERIFY001     | VerificationNotFoundException     | Verification token not found         |
| VERIFY002     | RateLimitExceededException        | Too many requests, wait before retry |
| VERIFY003     | InvalidVerificationCodeException  | Invalid verification code            |
| VERIFY004     | VerificationTokenExpiredException | Verification token expired           |
| VERIFY005     | TooManyAttemptsException          | Too many verification attempts       |
| SURVEY001     | InsufficientBalanceException      | Not enough balance                   |
| SURVEY002     | SurveyCreationException           | Failed to create survey              |
| SURVEY003     | MaxResponsesReachedException      | Maximum responses reached            |
| SURVEY004     | CannotParticipateSelfException    | Cannot participate in own survey     |
| SURVEY005     | SurveyNotFoundException           | Survey not found                     |
| GOOGLE001     | GoogleAccountNotFoundException    | Google account not found             |
| FORM001       | InvalidFormUrlException           | Invalid Google Form URL              |
| FORM002       | FormAccessDeniedException         | No access to form                    |
| SERVER001     | InternalServerError               | Internal server error                |

---

## Notes for Frontend Developers

1. **Authentication**: Most endpoints require authentication. Include the `Authorization: Bearer <token>` header with the access token obtained from login or email verification.

2. **Token Expiration**: Access tokens expire after 30 minutes (1800 seconds). Implement token refresh logic using the refresh token.

3. **Error Handling**: Always check the `error.code` field to handle specific error cases appropriately in your UI.

4. **Pagination**: Endpoints that return lists support `skip` and `limit` query parameters for pagination.

5. **Email Verification Flow**:

   - Register → Receive verification_token
   - Request verification code → Code sent to email
   - Verify email with code → Receive access/refresh tokens

6. **Survey Participation Flow**:

   - Browse surveys → Choose survey
   - Start participation → Receive Google Form URL
   - Complete Google Form (external)
   - Verify completion → Receive reward points

7. **Balance Management**: Users need sufficient balance to create surveys. The required balance is calculated as: `reward_per_response * responses_needed`

8. **Google Account Integration**: Users must connect at least one Google account to create surveys. The Google account is used to access and manage Google Forms.
