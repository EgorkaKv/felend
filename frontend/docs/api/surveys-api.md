## Surveys

### Table of Contents

- [GET /surveys](#get-surveys) - Get feed of active surveys (public)
- [GET /surveys/my/](#get-surveysmy) - Get surveys created by authenticated user
- [POST /surveys/validate](#post-surveysvalidate) - Validate Google Form URL and access
- [POST /surveys/my/](#post-surveysmy) - Create a new survey
- [GET /surveys/my/{survey_id}](#get-surveysmysurvey_id) - Get details of user's survey
- [PUT /surveys/my/{survey_id}](#put-surveysmysurvey_id) - Update user's survey
- [DELETE /surveys/my/{survey_id}](#delete-surveysmysurvey_id) - Delete user's survey
- [POST /surveys/{survey_id}/participate](#post-surveyssurvey_idparticipate) - Start survey participation
- [POST /surveys/{survey_id}/verify](#post-surveyssurvey_idverify) - Verify survey completion
- [GET /surveys/{survey_id}/my-status](#get-surveyssurvey_idmy-status) - Get participation status
- [GET /surveys/my-responses](#get-surveysmy-responses) - Get user's survey responses

---

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