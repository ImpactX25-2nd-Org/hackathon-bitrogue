# 🚀 KrishiLok API Endpoints - Quick Reference

## Base URL
```
Development: http://localhost:3000/api
Production: https://api.krishilok.com/api
```

## Authentication
All protected endpoints require JWT token in header:
```
Authorization: Bearer <token>
```

---

## 📍 Endpoints Summary

### 🔐 Authentication
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/login` | User login | ❌ |
| POST | `/auth/register` | New user registration | ❌ |
| POST | `/auth/forgot-password` | Password recovery | ❌ |
| POST | `/auth/verify-otp` | Verify OTP | ❌ |
| POST | `/auth/reset-password` | Reset password | ❌ |
| GET | `/auth/me` | Get current user | ✅ |
| POST | `/auth/refresh` | Refresh token | ✅ |

---

### 🌾 Disease Detection
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/scan` | Upload crop image for detection | ✅ |
| GET | `/detection/:scanId` | Get detection result | ✅ |
| GET | `/detection/:scanId/audio?lang={code}` | Get TTS audio | ✅ |
| GET | `/scans` | Get user's scan history | ✅ |
| DELETE | `/scans/:scanId` | Delete scan | ✅ |

---

### 👥 Community
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/community/posts` | List all posts (with filters) | ✅ |
| POST | `/community/posts` | Create new post | ✅ |
| GET | `/community/posts/:postId` | Get single post with responses | ✅ |
| PUT | `/community/posts/:postId` | Update post | ✅ |
| DELETE | `/community/posts/:postId` | Delete post | ✅ |
| POST | `/community/posts/:postId/respond` | Add response to post | ✅ |
| POST | `/community/posts/:postId/resolve` | Mark as resolved | ✅ |
| POST | `/community/posts/:postId/view` | Increment view count | ✅ |

---

### 💡 Suggestions & Trust
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/suggestions/:scanId` | Get suggestions for disease | ✅ |
| POST | `/suggestions` | Create new suggestion | ✅ |
| POST | `/trust-score` | Submit trust score feedback | ✅ |
| GET | `/trust-scores?updated_after={ts}` | Get updated trust scores | ✅ |

---

### 🗣️ Voice & Translation
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/voice/transcribe` | Transcribe & translate audio | ✅ |
| POST | `/voice/tts` | Generate TTS audio | ✅ |

---

### 🔔 Notifications
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/notifications` | Get user notifications | ✅ |
| PUT | `/notifications/:id/read` | Mark as read | ✅ |
| POST | `/notifications/schedule` | Schedule notification (admin) | ✅ |

---

### 📊 Analytics (Admin/Stats)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/analytics/dashboard` | Dashboard stats | ✅ |
| GET | `/analytics/diseases` | Disease trends | ✅ |
| GET | `/analytics/users` | User statistics | ✅ |

---

## 📋 Detailed Endpoint Specs

### POST /api/auth/login
```http
POST /api/auth/login
Content-Type: application/json

{
  "identifier": "9876543210",
  "password": "password123",
  "language": "en"
}
```

**Response (200):**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "uuid",
    "name": "Ramesh Kumar",
    "phone": "9876543210",
    "email": "ramesh@example.com",
    "language": "en",
    "trustScore": 75
  }
}
```

---

### POST /api/scan
```http
POST /api/scan
Content-Type: multipart/form-data
Authorization: Bearer <token>

image: [File]
cropName: "Groundnut"
description: "Yellow spots on leaves"
voiceFile: [File] (optional)
language: "mr"
```

**Response (202):**
```json
{
  "scanId": "scan_uuid_123",
  "status": "processing",
  "estimatedTime": 20
}
```

---

### GET /api/detection/:scanId
```http
GET /api/detection/scan_uuid_123
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "scanId": "scan_uuid_123",
  "status": "completed",
  "diseaseName": "Early Blight (Alternaria solani)",
  "reliability": 92,
  "nextSteps": [
    "Remove and destroy infected leaves immediately",
    "Apply copper-based fungicide every 7-10 days"
  ],
  "isCommon": true,
  "imageUrl": "https://cdn.example.com/scans/...",
  "cropName": "Groundnut",
  "description": "Yellow spots on leaves",
  "communityAdvice": [
    {
      "id": "advice_uuid",
      "farmerName": "Suresh Deshmukh",
      "farmerAvatar": "https://...",
      "trustScore": 88,
      "advice": "I faced this same issue...",
      "helpfulCount": 24,
      "responseCount": 8,
      "timestamp": "2024-10-20T10:30:00Z"
    }
  ]
}
```

---

### GET /api/detection/:scanId/audio
```http
GET /api/detection/scan_uuid_123/audio?lang=mr
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "audioUrl": "https://cdn.example.com/audio/scan_uuid_123_mr.mp3",
  "language": "mr",
  "duration": 45
}
```

---

### GET /api/community/posts
```http
GET /api/community/posts?status=unresolved&page=1&limit=10&search=tomato
Authorization: Bearer <token>
```

**Query Parameters:**
- `status`: all | unresolved | resolved
- `page`: number (default: 1)
- `limit`: number (default: 10, max: 50)
- `search`: string
- `sortBy`: recent | popular | trending

**Response (200):**
```json
{
  "posts": [
    {
      "id": "post_uuid",
      "farmerId": "user_uuid",
      "farmerName": "Rajesh Kumar",
      "farmerAvatar": "https://...",
      "trustScore": 85,
      "title": "Yellowing leaves on tomato plants",
      "description": "My tomato plants are showing...",
      "imageUrl": "https://...",
      "cropName": "Tomato",
      "tags": ["Tomato", "Disease", "Urgent"],
      "responseCount": 12,
      "viewCount": 234,
      "isResolved": false,
      "timestamp": "2024-10-23T08:15:00Z",
      "createdAt": "2024-10-23T08:15:00Z"
    }
  ],
  "totalCount": 45,
  "page": 1,
  "hasMore": true
}
```

---

### POST /api/community/posts
```http
POST /api/community/posts
Content-Type: multipart/form-data
Authorization: Bearer <token>

title: "Help needed with cotton boll worm"
description: "I'm seeing boll worm infestation..."
cropName: "Cotton"
tags: "cotton,pest,organic"
image: [File] (optional)
scanId: "scan_uuid" (optional)
```

**Response (201):**
```json
{
  "success": true,
  "postId": "post_uuid",
  "post": {
    "id": "post_uuid",
    "farmerId": "user_uuid",
    "title": "Help needed with cotton boll worm",
    "description": "I'm seeing boll worm infestation...",
    "cropName": "Cotton",
    "tags": ["cotton", "pest", "organic"],
    "imageUrl": "https://...",
    "isResolved": false,
    "responseCount": 0,
    "viewCount": 0,
    "createdAt": "2024-10-25T12:30:00Z"
  }
}
```

---

### GET /api/community/posts/:postId
```http
GET /api/community/posts/post_uuid_123
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "post": {
    "id": "post_uuid_123",
    "farmerId": "user_uuid",
    "farmerName": "Rajesh Kumar",
    "farmerAvatar": "https://...",
    "trustScore": 85,
    "title": "Yellowing leaves on tomato plants",
    "description": "My tomato plants are showing yellow...",
    "imageUrl": "https://...",
    "cropName": "Tomato",
    "tags": ["Tomato", "Disease", "Urgent"],
    "responseCount": 12,
    "viewCount": 235,
    "isResolved": false,
    "createdAt": "2024-10-23T08:15:00Z"
  },
  "responses": [
    {
      "id": "response_uuid",
      "authorId": "user_uuid_2",
      "authorName": "Kavita Naik",
      "authorAvatar": "https://...",
      "trustScore": 95,
      "content": "This looks like early blight...",
      "isVerified": true,
      "verificationReason": "Recommendation matches agricultural best practices",
      "helpfulCount": 8,
      "timestamp": "2024-10-23T09:20:00Z",
      "role": "farmer"
    }
  ]
}
```

---

### POST /api/community/posts/:postId/respond
```http
POST /api/community/posts/post_uuid_123/respond
Content-Type: application/json
Authorization: Bearer <token>

{
  "content": "I suggest using neem oil spray...",
  "isExpertAdvice": false
}
```

**Response (201):**
```json
{
  "success": true,
  "responseId": "response_uuid",
  "aiVerification": {
    "isVerified": true,
    "confidence": 0.89,
    "reason": "Recommendation aligns with organic pest control practices"
  }
}
```

---

### POST /api/community/posts/:postId/resolve
```http
POST /api/community/posts/post_uuid_123/resolve
Content-Type: application/json
Authorization: Bearer <token>

{
  "acceptedResponseId": "response_uuid"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Post marked as resolved",
  "trustScoreUpdated": true
}
```

---

### GET /api/suggestions/:scanId
```http
GET /api/suggestions/scan_uuid_123
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "suggestions": [
    {
      "id": "suggestion_uuid",
      "text": "Apply Mancozeb fungicide twice with 10 days gap",
      "author": {
        "id": "user_uuid",
        "name": "Suresh Deshmukh",
        "avatar": "https://..."
      },
      "usefulness": 85,
      "details": "I faced this same issue last month. Applied Mancozeb...",
      "farmerId": "user_uuid"
    }
  ]
}
```

---

### POST /api/trust-score
```http
POST /api/trust-score
Content-Type: application/json
Authorization: Bearer <token>

{
  "suggestionId": "suggestion_uuid",
  "score": 4,
  "feedback": "This solution worked perfectly!",
  "scanId": "scan_uuid"
}
```

**Response (200):**
```json
{
  "success": true,
  "newTrustScore": 87,
  "followUpScheduled": true,
  "followUpDate": "2024-11-05T10:00:00Z"
}
```

---

### POST /api/voice/transcribe
```http
POST /api/voice/transcribe
Content-Type: multipart/form-data
Authorization: Bearer <token>

audioFile: [File]
sourceLanguage: "mr"
```

**Response (200):**
```json
{
  "transcription": "माझ्या टोमॅटोच्या झाडांवर पिवळे डाग आहेत",
  "translation": "My tomato plants have yellow spots",
  "sourceLanguage": "mr",
  "confidence": 0.92
}
```

---

### GET /api/notifications
```http
GET /api/notifications?unreadOnly=true
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "notifications": [
    {
      "id": "notif_uuid",
      "type": "trust_score_followup",
      "title": "How did it work?",
      "message": "Did Suresh Deshmukh's suggestion help solve your crop issue?",
      "isRead": false,
      "createdAt": "2024-10-25T10:00:00Z",
      "metadata": {
        "suggestionId": "suggestion_uuid",
        "scanId": "scan_uuid",
        "farmerName": "Suresh Deshmukh"
      }
    }
  ]
}
```

---

## 🔒 Error Responses

### 401 Unauthorized
```json
{
  "success": false,
  "error": {
    "code": "AUTH_TOKEN_EXPIRED",
    "message": "Your session has expired. Please login again."
  }
}
```

### 400 Bad Request
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": "cropName is required",
    "field": "cropName"
  }
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Scan not found"
  }
}
```

### 429 Rate Limited
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "retryAfter": 60
  }
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred. Please try again."
  }
}
```

---

## 📝 Common HTTP Status Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST (resource created) |
| 202 | Accepted | Async operation started (scan processing) |
| 400 | Bad Request | Invalid input/validation error |
| 401 | Unauthorized | Missing or invalid auth token |
| 403 | Forbidden | Valid token but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource (e.g., email exists) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | Server overloaded or maintenance |

---

## 🎯 Rate Limiting

| Endpoint Type | Limit | Window |
|--------------|-------|--------|
| Authentication | 5 requests | 1 minute |
| Scan Upload | 10 requests | 1 minute |
| Community Posts | 20 requests | 1 minute |
| General API | 100 requests | 1 minute |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1698249600
```

---

## 🌐 Multi-Language Support

All endpoints that return text content should accept `Accept-Language` header:
```
Accept-Language: mr
```

Supported language codes:
- `en` - English
- `ta` - Tamil
- `mr` - Marathi
- `kn` - Kannada
- `hi` - Hindi
- `te` - Telugu

---

## 📦 Pagination

List endpoints support pagination:

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10, max: 50)

**Response includes:**
```json
{
  "data": [...],
  "totalCount": 150,
  "page": 2,
  "hasMore": true
}
```

---

## 🔍 Filtering & Sorting

### Community Posts Filters
```
?status=unresolved
?cropName=tomato
?tags=pest,disease
?userId=uuid
?sortBy=recent|popular|trending
```

### Scan History Filters
```
?status=completed|processing|failed
?cropName=cotton
?fromDate=2024-10-01
?toDate=2024-10-31
```

---

## 🧪 Testing Endpoints

### Health Check
```http
GET /health
```
Response:
```json
{
  "status": "ok",
  "timestamp": "2024-10-25T12:00:00Z",
  "version": "1.0.0"
}
```

### Database Status
```http
GET /health/db
```
Response:
```json
{
  "database": "connected",
  "redis": "connected",
  "mlModel": "online"
}
```

---

## 📚 Additional Resources

- Full Documentation: `BACKEND_REQUIREMENTS_REPORT.md`
- Frontend Code: `frontend/src/lib/api-placeholders.ts`
- Postman Collection: TBD
- OpenAPI Spec: TBD

---

**Last Updated:** 2025-10-25  
**API Version:** 1.0.0  
**Status:** Ready for Implementation ✅
