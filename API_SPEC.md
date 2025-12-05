# API Specification

## Overview

Bakhmach Business Hub REST API provides comprehensive endpoints for managing Personal Development Plans (PDPs), goals, tasks, and analytics. The API follows OpenAPI 3.0 specification and emphasizes security, rate limiting, and comprehensive documentation.

**Base URL:** `https://api.bakhmach-hub.local/v1`

**Authentication:** JWT Bearer Token (required for all endpoints except `/auth/register` and `/auth/login`)

---

## Authentication

### POST /auth/register

Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "role": "user"
}
```

**Response (201):**
```json
{
  "id": "usr_123456",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### POST /auth/login

Authenticate user and receive JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

### POST /auth/refresh

Refresh expired access token.

**Headers:**
```
Authorization: Bearer {refresh_token}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

### POST /auth/logout

Invalidate user tokens.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

---

## Personal Development Plans (PDPs)

### GET /pdps

Retrieve all PDPs for the authenticated user.

**Query Parameters:**
- `status` (optional): active, completed, archived
- `skip` (optional): Number of items to skip (default: 0)
- `limit` (optional): Number of items to return (default: 20, max: 100)

**Response (200):**
```json
{
  "items": [
    {
      "id": "pdp_001",
      "user_id": "usr_123456",
      "title": "2024 Business Growth",
      "description": "Comprehensive plan for expanding business operations",
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "target_completion": "2024-12-31T23:59:59Z"
    }
  ],
  "total": 5,
  "skip": 0,
  "limit": 20
}
```

### POST /pdps

Create a new Personal Development Plan.

**Request:**
```json
{
  "title": "2024 Business Growth",
  "description": "Comprehensive plan for expanding business operations",
  "target_completion": "2024-12-31T23:59:59Z"
}
```

**Response (201):**
```json
{
  "id": "pdp_001",
  "user_id": "usr_123456",
  "title": "2024 Business Growth",
  "description": "Comprehensive plan for expanding business operations",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z",
  "target_completion": "2024-12-31T23:59:59Z"
}
```

### GET /pdps/{pdp_id}

Retrieve a specific PDP with all associated goals.

**Response (200):**
```json
{
  "id": "pdp_001",
  "user_id": "usr_123456",
  "title": "2024 Business Growth",
  "description": "Comprehensive plan for expanding business operations",
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "target_completion": "2024-12-31T23:59:59Z",
  "goals": []
}
```

### PUT /pdps/{pdp_id}

Update an existing PDP.

**Request:**
```json
{
  "title": "2024 Business Growth - Updated",
  "status": "active"
}
```

**Response (200):** Updated PDP object

### DELETE /pdps/{pdp_id}

Delete a PDP.

**Response (204):** No content

---

## Goals

### GET /goals?pdp_id={pdp_id}

Retrieve all goals within a PDP.

**Response (200):**
```json
{
  "items": [
    {
      "id": "goal_001",
      "pdp_id": "pdp_001",
      "title": "Increase Revenue by 50%",
      "description": "Implement new market strategies",
      "status": "in_progress",
      "priority": "high",
      "target_date": "2024-06-30T23:59:59Z",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### POST /goals

Create a new goal within a PDP.

**Request:**
```json
{
  "pdp_id": "pdp_001",
  "title": "Increase Revenue by 50%",
  "description": "Implement new market strategies",
  "priority": "high",
  "target_date": "2024-06-30T23:59:59Z"
}
```

**Response (201):** Created goal object

### PUT /goals/{goal_id}

Update a goal.

**Request:**
```json
{
  "status": "completed",
  "priority": "high"
}
```

**Response (200):** Updated goal object

### DELETE /goals/{goal_id}

Delete a goal.

**Response (204):** No content

---

## Tasks

### GET /tasks?goal_id={goal_id}

Retrieve all tasks within a goal.

**Response (200):** Array of task objects

### POST /tasks

Create a new task.

**Request:**
```json
{
  "goal_id": "goal_001",
  "title": "Complete market analysis",
  "description": "Research new market opportunities",
  "status": "pending",
  "priority": "high",
  "due_date": "2024-02-15T23:59:59Z"
}
```

**Response (201):** Created task object

### PUT /tasks/{task_id}

Update a task.

**Response (200):** Updated task object

### DELETE /tasks/{task_id}

Delete a task.

**Response (204):** No content

---

## Analytics

### GET /analytics/pdp-progress

Get progress analytics for a PDP.

**Query Parameters:**
- `pdp_id`: The PDP to analyze

**Response (200):**
```json
{
  "pdp_id": "pdp_001",
  "total_goals": 10,
  "completed_goals": 3,
  "in_progress_goals": 5,
  "pending_goals": 2,
  "completion_percentage": 30,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

### GET /analytics/user-stats

Get overall user statistics.

**Response (200):**
```json
{
  "total_pdps": 5,
  "active_pdps": 3,
  "completed_pdps": 2,
  "total_goals": 50,
  "completed_goals": 15,
  "total_tasks": 200,
  "completed_tasks": 60
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "INVALID_REQUEST",
  "message": "Invalid request parameters",
  "details": {"email": "Invalid email format"}
}
```

### 401 Unauthorized
```json
{
  "error": "UNAUTHORIZED",
  "message": "Missing or invalid authentication token"
}
```

### 403 Forbidden
```json
{
  "error": "FORBIDDEN",
  "message": "User does not have permission to access this resource"
}
```

### 404 Not Found
```json
{
  "error": "NOT_FOUND",
  "message": "Requested resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Validation failed",
  "details": {"title": "Title is required"}
}
```

### 500 Internal Server Error
```json
{
  "error": "INTERNAL_ERROR",
  "message": "An unexpected error occurred"
}
```

---

## Rate Limiting

**Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1705324200
```

**Rate Limits:**
- 1000 requests per hour per API key
- 100 requests per minute per IP address

---

## Pagination

All list endpoints support pagination with `skip` and `limit` query parameters.

**Default:** skip=0, limit=20
**Maximum:** limit=100

---

## Timestamps

All timestamps are in ISO 8601 format (UTC): `YYYY-MM-DDTHH:mm:ssZ`

---

For detailed implementation examples and testing, refer to QUICK_START.md
