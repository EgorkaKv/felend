## Google Accounts

### Table of Contents

- [GET /google-accounts](#get-google-accounts) - List all linked Google accounts
- [GET /google-accounts/connect](#get-google-accountsconnect) - Initiate Google OAuth for linking account
- [GET /google-accounts/callback](#get-google-accountscallback) - Google OAuth callback for account linking
- [POST /google-accounts/{account_id}/set-primary](#post-google-accountsaccount_idset-primary) - Set Google account as primary
- [POST /google-accounts/{account_id}/disconnect](#post-google-accountsaccount_iddisconnect) - Disconnect Google account
- [GET /google-accounts/google/status](#get-google-accountsgooglestatus) - Check Google connection status

---

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

### GET /google-accounts/connect

Initiate Google OAuth flow for linking a Google account to the current authenticated user (for Google Forms access). Requires a `redirect_uri` query parameter.

**Query Parameters:**

- `redirect_uri` (required): Frontend URL for redirect after OAuth completion

**Request:**

```
GET /api/v1/google-accounts/connect?redirect_uri=http://localhost:5173/google-accounts/success
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**

```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=...&redirect_uri=...&scope=...&state=...",
  "message": "Перейдите по ссылке для авторизации в Google",
  "user_id": 1
}
```

**Note:** Frontend should redirect user to `authorization_url` using `window.location.href`.

**Error Responses:**

**401 Unauthorized - Not Authenticated:**

```json
{
  "error": {
    "message": "Not authenticated",
    "code": "AUTH004",
    "type": "NotAuthenticatedException",
    "details": null,
    "timestamp": "2025-10-29T12:00:00Z",
    "path": "/api/v1/google-accounts/connect"
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
    "timestamp": "2025-10-29T12:00:00Z",
    "path": "/api/v1/google-accounts/connect"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Ошибка при инициализации Google авторизации",
    "code": "SERVER001",
    "type": "InternalServerError",
    "details": null,
    "timestamp": "2025-10-29T12:00:00Z",
    "path": "/api/v1/google-accounts/connect"
  }
}
```

---

### GET /google-accounts/callback

Google OAuth callback endpoint for account linking. Handles the authorization code from Google, links the Google account to the user, and redirects to the frontend with result parameters.

**Query Parameters:**

- `code` (required): Authorization code from Google
- `state` (required): JWT state token containing user_id and frontend_redirect_uri
- `scope` (optional): Scopes granted during authorization

**Response (302 Found):**

Redirects to the `redirect_uri` specified in `/connect` with result parameters:

**Success Redirect:**
```
http://localhost:5173/google-accounts/success?google_connected=success&email=student@gmail.com
```

**Error Redirect:**
```
http://localhost:5173/google-accounts/success?google_connected=error&error_code=account_already_connected&message=This+Google+account+is+already+connected+to+your+account
```

**Error Codes:**

| Error Code | Description |
|------------|-------------|
| `invalid_state` | Invalid or expired state parameter |
| `user_not_found` | User not found |
| `account_already_connected` | This Google account is already connected to your account |
| `account_connected_to_another_user` | This Google account is already connected to another user |
| `google_api_error` | Failed to retrieve data from Google or Google API error |
| `internal_error` | An unexpected error occurred |

**Error Responses:**

**500 Internal Server Error (only when redirect_uri is missing):**

```json
{
  "error": {
    "message": "Failed to process Google OAuth callback",
    "code": "SERVER001",
    "type": "InternalServerError",
    "details": null,
    "timestamp": "2025-10-29T12:00:00Z",
    "path": "/api/v1/google-accounts/callback"
  }
}
```

---

### POST /google-accounts/{account_id}/set-primary

Set a specific Google account as the primary account for the authenticated user.

**Request:**

```
POST /api/v1/google-accounts/5/set-primary
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**

```json
{
  "message": "Основной Google аккаунт изменен",
  "primary_account": {
    "id": 5,
    "email": "student@gmail.com",
    "name": "John Doe"
  }
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
    "timestamp": "2025-10-29T12:00:00Z",
    "path": "/api/v1/google-accounts/5/set-primary"
  }
}
```

**404 Not Found - Google Account Not Found:**

```json
{
  "error": {
    "message": "Google аккаунт не найден",
    "code": "GOOGLE001",
    "type": "GoogleAccountNotFoundException",
    "details": {
      "google_account_id": 5
    },
    "timestamp": "2025-10-29T12:00:00Z",
    "path": "/api/v1/google-accounts/5/set-primary"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Ошибка при установке основного аккаунта",
    "code": "SERVER001",
    "type": "InternalServerError",
    "details": null,
    "timestamp": "2025-10-29T12:00:00Z",
    "path": "/api/v1/google-accounts/5/set-primary"
  }
}
```

---

### POST /google-accounts/{account_id}/disconnect

Disconnect a specific Google account from the authenticated user.

**Request:**

```
POST /api/v1/google-accounts/5/disconnect
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**

```json
{
  "message": "Google аккаунт отключен",
  "disconnected_account_id": 5
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
    "timestamp": "2025-10-29T12:00:00Z",
    "path": "/api/v1/google-accounts/5/disconnect"
  }
}
```

**404 Not Found - Google Account Not Found:**

```json
{
  "error": {
    "message": "Google аккаунт не найден",
    "code": "GOOGLE001",
    "type": "GoogleAccountNotFoundException",
    "details": {
      "google_account_id": 5
    },
    "timestamp": "2025-10-29T12:00:00Z",
    "path": "/api/v1/google-accounts/5/disconnect"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Ошибка при отключении Google аккаунта",
    "code": "SERVER001",
    "type": "InternalServerError",
    "details": null,
    "timestamp": "2025-10-29T12:00:00Z",
    "path": "/api/v1/google-accounts/5/disconnect"
  }
}
```

---

### GET /google-accounts/google/status

Check the Google account connection status for the authenticated user, including total accounts and primary account details.

**Request:**

```
GET /api/v1/google-accounts/google/status
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**

```json
{
  "google_connected": true,
  "total_accounts": 2,
  "primary_account": {
    "id": 5,
    "email": "student@gmail.com",
    "name": "John Doe",
    "token_valid": true,
    "expires_at": "2025-11-29T12:00:00Z"
  }
}
```

**Response (200 OK) - No Google Accounts:**

```json
{
  "google_connected": false,
  "total_accounts": 0,
  "primary_account": null
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
    "timestamp": "2025-10-29T12:00:00Z",
    "path": "/api/v1/google-accounts/google/status"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "message": "Ошибка при проверке статуса Google подключения",
    "code": "SERVER001",
    "type": "InternalServerError",
    "details": null,
    "timestamp": "2025-10-29T12:00:00Z",
    "path": "/api/v1/google-accounts/google/status"
  }
}
```