## Users

### Table of Contents

- [GET /users/me](#get-usersme) - Get current user's profile
- [PUT /users/me](#put-usersme) - Update current user's profile
- [GET /users/me/transactions](#get-usersmetransactions) - Get user's transaction history

---

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