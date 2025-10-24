# 🌾 KrishiLok - Comprehensive Backend Requirements Report

## 📋 Executive Summary

**Project Name:** KrishiLok  
**Type:** Agricultural Community Support Platform  
**Frontend Stack:** React + TypeScript + Vite + TanStack Query + React Router  
**Primary Goal:** AI-powered crop disease detection with community-driven knowledge sharing and trust-based recommendation system

---

## 🎯 Application Overview

KrishiLok is a multi-language agricultural platform connecting farmers with:
- **AI-powered disease detection** using ML models
- **Community knowledge sharing** with trust scores
- **Multi-language support** (English, Tamil, Marathi, Kannada, Hindi, Telugu)
- **Voice recording** with auto-translation capabilities
- **Trust-based recommendation system** for verified agricultural advice

---

## 🗺️ Frontend Route Structure

### Public Routes
1. **`/`** - Home/Landing Page
2. **`/login`** - Authentication Page

### Protected Routes
3. **`/dashboard`** - Main Dashboard (Disease Detection + Community)
4. **`/crop-scan`** - Crop Scanning & Upload Interface
5. **`/documentation`** - Crop Information Database
6. **`*`** - 404 Not Found

---

## 🔌 API Endpoints Required

### 1. Authentication & User Management

#### `POST /api/auth/login`
**Purpose:** User authentication  
**Request Body:**
```json
{
  "identifier": "string (phone or email)",
  "password": "string",
  "language": "string (language code: en, ta, mr, kn, hi, te)"
}
```
**Response:**
```json
{
  "success": true,
  "token": "string (JWT token)",
  "user": {
    "id": "string",
    "name": "string",
    "phone": "string",
    "email": "string",
    "language": "string",
    "trustScore": "number (0-100)"
  }
}
```
**Error Response:**
```json
{
  "success": false,
  "error": "string (error message)"
}
```

#### `POST /api/auth/register`
**Purpose:** New user registration  
**Request Body:**
```json
{
  "name": "string",
  "phone": "string",
  "email": "string (optional)",
  "password": "string",
  "language": "string"
}
```
**Response:** Same as login

#### `POST /api/auth/forgot-password`
**Purpose:** Password recovery via OTP  
**Request Body:**
```json
{
  "identifier": "string (phone or email)"
}
```
**Response:**
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "otpSentTo": "string (masked phone/email)"
}
```

---

### 2. Crop Disease Detection

#### `POST /api/scan`
**Purpose:** Upload crop image for disease detection  
**Content-Type:** `multipart/form-data`  
**Request Body:**
```
image: File (JPEG/PNG, max 10MB)
cropName: string
description: string
voiceFile: File (audio/webm, optional)
language: string
```
**Response:**
```json
{
  "scanId": "string (unique scan ID)",
  "status": "processing | completed",
  "estimatedTime": "number (seconds, if processing)"
}
```
**Backend Requirements:**
- Store image in cloud storage (AWS S3/GCP/Azure)
- Queue ML processing job (async)
- Store voice file if provided
- Transcribe and translate voice to English
- Return immediately with scanId for polling

#### `GET /api/detection/:scanId`
**Purpose:** Get disease detection result  
**Response:**
```json
{
  "scanId": "string",
  "status": "processing | completed | failed",
  "diseaseName": "string",
  "reliability": "number (0-100)",
  "nextSteps": ["string array of recommendations"],
  "isCommon": "boolean",
  "imageUrl": "string",
  "cropName": "string",
  "description": "string",
  "communityAdvice": [
    {
      "id": "string",
      "farmerName": "string",
      "farmerAvatar": "string (URL)",
      "trustScore": "number",
      "advice": "string",
      "helpfulCount": "number",
      "responseCount": "number",
      "timestamp": "string (ISO date)"
    }
  ]
}
```
**Backend Requirements:**
- If isCommon = true, include community advice from farmers with high trust scores
- Rank advice by usefulness/trust score
- Filter for this specific disease

#### `GET /api/detection/:scanId/audio?lang={languageCode}`
**Purpose:** Get text-to-speech audio of detection result  
**Query Params:**
- `lang`: Language code (ta, mr, kn, hi, te, en)

**Response:**
```json
{
  "audioUrl": "string (CDN/cloud storage URL)",
  "language": "string",
  "duration": "number (seconds)"
}
```
**Backend Requirements:**
- Use TTS service (Google Cloud TTS / AWS Polly / Azure TTS)
- Support Indian language voices
- Cache generated audio files
- Return publicly accessible URL

---

### 3. Community Features

#### `GET /api/community/posts`
**Purpose:** Fetch community posts with filters  
**Query Params:**
- `status`: all | unresolved | resolved
- `search`: string
- `page`: number
- `limit`: number
- `sortBy`: recent | popular | trending

**Response:**
```json
{
  "posts": [
    {
      "id": "string",
      "farmerId": "string",
      "farmerName": "string",
      "farmerAvatar": "string",
      "trustScore": "number",
      "title": "string",
      "description": "string",
      "imageUrl": "string (optional)",
      "cropName": "string",
      "tags": ["string array"],
      "responseCount": "number",
      "viewCount": "number",
      "isResolved": "boolean",
      "timestamp": "string (ISO date)",
      "createdAt": "string (ISO date)"
    }
  ],
  "totalCount": "number",
  "page": "number",
  "hasMore": "boolean"
}
```

#### `POST /api/community/posts`
**Purpose:** Create new community post  
**Content-Type:** `multipart/form-data`  
**Request Body:**
```
title: string
description: string
cropName: string
tags: string (comma-separated)
image: File (optional)
scanId: string (optional, if sharing from detection)
```
**Response:**
```json
{
  "success": true,
  "postId": "string",
  "post": { /* full post object */ }
}
```

#### `GET /api/community/posts/:postId`
**Purpose:** Get single post with all responses  
**Response:**
```json
{
  "post": { /* full post object */ },
  "responses": [
    {
      "id": "string",
      "authorId": "string",
      "authorName": "string",
      "authorAvatar": "string",
      "trustScore": "number",
      "content": "string",
      "isVerified": "boolean (AI verified)",
      "verificationReason": "string",
      "helpfulCount": "number",
      "timestamp": "string",
      "role": "farmer | expert | extension_worker"
    }
  ]
}
```

#### `POST /api/community/posts/:postId/respond`
**Purpose:** Add response to a post  
**Request Body:**
```json
{
  "content": "string",
  "isExpertAdvice": "boolean"
}
```
**Response:**
```json
{
  "success": true,
  "responseId": "string",
  "aiVerification": {
    "isVerified": "boolean",
    "confidence": "number",
    "reason": "string"
  }
}
```
**Backend Requirements:**
- Run AI verification on response content
- Check against agricultural databases
- Validate pesticide/fertilizer recommendations
- Flag potentially harmful advice

#### `POST /api/community/posts/:postId/resolve`
**Purpose:** Mark post as resolved  
**Request Body:**
```json
{
  "acceptedResponseId": "string"
}
```
**Response:**
```json
{
  "success": true
}
```
**Backend Requirements:**
- Update farmer's trust score who gave accepted response
- Trigger trust score recalculation

---

### 4. Suggestions & Trust Score System

#### `GET /api/suggestions/:scanId`
**Purpose:** Get community suggestions for a specific disease/scan  
**Response:**
```json
{
  "suggestions": [
    {
      "id": "string",
      "text": "string",
      "author": {
        "id": "string",
        "name": "string",
        "avatar": "string"
      },
      "usefulness": "number (0-100)",
      "details": "string",
      "farmerId": "string"
    }
  ]
}
```
**Backend Requirements:**
- Fetch suggestions based on disease name/category
- Rank by usefulness score and trust score
- Include detailed implementation steps

#### `POST /api/trust-score`
**Purpose:** Submit feedback for a suggestion  
**Request Body:**
```json
{
  "suggestionId": "string",
  "score": "number (1-5)",
  "feedback": "string (optional)",
  "scanId": "string"
}
```
**Response:**
```json
{
  "success": true,
  "newTrustScore": "number",
  "followUpScheduled": "boolean",
  "followUpDate": "string (ISO date)"
}
```
**Backend Requirements:**
- Update farmer's trust score using weighted algorithm
- Schedule follow-up notification for 10-15 days
- Store feedback for future AI training
- Recalculate suggestion usefulness scores

#### `GET /api/trust-scores?updated_after={timestamp}`
**Purpose:** Get updated trust scores for dashboard refresh  
**Response:**
```json
{
  "farmers": [
    {
      "id": "string",
      "trustScore": "number"
    }
  ],
  "lastUpdate": "string (ISO date)"
}
```

---

### 5. Voice & Translation

#### `POST /api/voice/transcribe`
**Purpose:** Transcribe voice recording and translate  
**Content-Type:** `multipart/form-data`  
**Request Body:**
```
audioFile: File (audio/webm)
sourceLanguage: string (language code)
```
**Response:**
```json
{
  "transcription": "string (original language)",
  "translation": "string (English)",
  "sourceLanguage": "string",
  "confidence": "number (0-1)"
}
```
**Backend Requirements:**
- Use Google Speech-to-Text or similar API
- Support Indian languages (ta, mr, kn, hi, te)
- Translate to English using Google Translate API
- Store both original and translated text

---

### 6. Follow-up & Notifications

#### `POST /api/notifications/schedule`
**Purpose:** Schedule follow-up notification  
**Request Body:**
```json
{
  "userId": "string",
  "type": "trust_score_followup | general",
  "scheduledFor": "string (ISO date)",
  "metadata": {
    "suggestionId": "string",
    "scanId": "string"
  }
}
```
**Response:**
```json
{
  "success": true,
  "notificationId": "string"
}
```

#### `GET /api/notifications`
**Purpose:** Get user notifications  
**Response:**
```json
{
  "notifications": [
    {
      "id": "string",
      "type": "string",
      "title": "string",
      "message": "string",
      "isRead": "boolean",
      "createdAt": "string",
      "metadata": {}
    }
  ]
}
```

---

## 🗄️ Database Schema Requirements

### Users Table
```sql
users {
  id: UUID PRIMARY KEY
  name: VARCHAR(255) NOT NULL
  phone: VARCHAR(20) UNIQUE
  email: VARCHAR(255) UNIQUE
  password_hash: VARCHAR(255) NOT NULL
  language: VARCHAR(5) DEFAULT 'en'
  trust_score: DECIMAL(5,2) DEFAULT 50.0
  role: ENUM('farmer', 'expert', 'extension_worker')
  avatar_url: TEXT
  created_at: TIMESTAMP
  updated_at: TIMESTAMP
}
```

### Scans Table
```sql
scans {
  id: UUID PRIMARY KEY
  user_id: UUID FOREIGN KEY REFERENCES users(id)
  crop_name: VARCHAR(100)
  description: TEXT
  image_url: TEXT NOT NULL
  voice_file_url: TEXT
  transcription: TEXT
  status: ENUM('processing', 'completed', 'failed')
  disease_name: VARCHAR(255)
  reliability: DECIMAL(5,2)
  next_steps: JSONB
  is_common: BOOLEAN
  language: VARCHAR(5)
  created_at: TIMESTAMP
  updated_at: TIMESTAMP
}
```

### Community Posts Table
```sql
community_posts {
  id: UUID PRIMARY KEY
  user_id: UUID FOREIGN KEY REFERENCES users(id)
  title: VARCHAR(500) NOT NULL
  description: TEXT NOT NULL
  crop_name: VARCHAR(100)
  image_url: TEXT
  scan_id: UUID FOREIGN KEY REFERENCES scans(id)
  tags: TEXT[] (array of strings)
  is_resolved: BOOLEAN DEFAULT false
  accepted_response_id: UUID
  view_count: INTEGER DEFAULT 0
  response_count: INTEGER DEFAULT 0
  created_at: TIMESTAMP
  updated_at: TIMESTAMP
}
```

### Post Responses Table
```sql
post_responses {
  id: UUID PRIMARY KEY
  post_id: UUID FOREIGN KEY REFERENCES community_posts(id)
  user_id: UUID FOREIGN KEY REFERENCES users(id)
  content: TEXT NOT NULL
  is_verified: BOOLEAN DEFAULT false
  verification_reason: TEXT
  verification_confidence: DECIMAL(3,2)
  helpful_count: INTEGER DEFAULT 0
  is_expert_advice: BOOLEAN DEFAULT false
  created_at: TIMESTAMP
  updated_at: TIMESTAMP
}
```

### Suggestions Table
```sql
suggestions {
  id: UUID PRIMARY KEY
  disease_name: VARCHAR(255) NOT NULL
  user_id: UUID FOREIGN KEY REFERENCES users(id)
  text: TEXT NOT NULL
  details: TEXT
  usefulness_score: DECIMAL(5,2) DEFAULT 50.0
  usage_count: INTEGER DEFAULT 0
  created_at: TIMESTAMP
  updated_at: TIMESTAMP
}
```

### Trust Score Feedback Table
```sql
trust_feedback {
  id: UUID PRIMARY KEY
  suggestion_id: UUID FOREIGN KEY REFERENCES suggestions(id)
  user_id: UUID FOREIGN KEY REFERENCES users(id) (who gave feedback)
  farmer_id: UUID FOREIGN KEY REFERENCES users(id) (whose suggestion)
  score: INTEGER (1-5)
  feedback_text: TEXT
  scan_id: UUID FOREIGN KEY REFERENCES scans(id)
  created_at: TIMESTAMP
}
```

### Notifications Table
```sql
notifications {
  id: UUID PRIMARY KEY
  user_id: UUID FOREIGN KEY REFERENCES users(id)
  type: VARCHAR(50)
  title: VARCHAR(255)
  message: TEXT
  metadata: JSONB
  is_read: BOOLEAN DEFAULT false
  scheduled_for: TIMESTAMP
  sent_at: TIMESTAMP
  created_at: TIMESTAMP
}
```

---

## 🤖 AI/ML Integration Requirements

### 1. Disease Detection Model
**Inputs:**
- Crop image (preprocessed to standard size, e.g., 224x224 or 512x512)
- Crop name/category

**Outputs:**
- Disease name (string)
- Confidence score (0-100)
- Is common disease (boolean)
- Recommended actions (array of strings)

**Integration:**
- Use REST API or gRPC endpoint
- Async processing with job queue (Redis/RabbitMQ)
- Store model predictions in database
- Version control for model updates

### 2. AI Verification for Community Responses
**Inputs:**
- Response text
- Crop name
- Disease context

**Outputs:**
- Is verified (boolean)
- Confidence score (0-1)
- Verification reason (string)
- Flagged concerns (array)

**Checks:**
- Pesticide dosage validation against safe limits
- Crop-specific recommendation validation
- Contradictory advice detection
- Harmful chemical detection

### 3. Voice Recognition & Translation
**Services Required:**
- **Speech-to-Text:** Google Cloud Speech-to-Text API or AWS Transcribe
- **Translation:** Google Cloud Translation API or AWS Translate
- **Text-to-Speech:** Google Cloud TTS, AWS Polly, or Azure TTS

**Supported Languages:**
- Tamil (ta-IN)
- Marathi (mr-IN)
- Kannada (kn-IN)
- Hindi (hi-IN)
- Telugu (te-IN)
- English (en-IN)

---

## 🔐 Security Requirements

### Authentication
- JWT-based authentication
- Token expiry: 24 hours (access token)
- Refresh token: 30 days
- Password hashing: bcrypt (12 rounds minimum)

### File Upload Security
- Validate file types (MIME type checking)
- Scan for malware
- Size limits: Images (10MB), Audio (5MB)
- Generate unique filenames (UUID-based)
- Store in isolated cloud storage

### API Rate Limiting
- Per user: 100 requests/minute
- Anonymous: 20 requests/minute
- ML endpoints: 10 requests/minute per user

### Data Privacy
- Encrypt sensitive user data
- GDPR compliance (data deletion on request)
- Anonymize data for ML training
- Secure image URLs with signed tokens (if needed)

---

## 📱 Multi-Language Support

### Language Context
The frontend stores user's language preference in:
1. **LocalStorage:** `preferredLanguage` key
2. **LanguageContext:** React context provider
3. **All API calls include:** `language` parameter

### Backend Translation Requirements
1. **Static content translation:**
   - Disease names
   - Recommendations
   - UI messages
   - Error messages

2. **Dynamic content:**
   - Use language code in database queries
   - Store translations in separate table or use i18n service

3. **Supported Languages:**
   ```json
   [
     { "code": "en", "name": "English", "nativeName": "English" },
     { "code": "ta", "name": "Tamil", "nativeName": "தமிழ்" },
     { "code": "mr", "name": "Marathi", "nativeName": "मराठी" },
     { "code": "kn", "name": "Kannada", "nativeName": "ಕನ್ನಡ" },
     { "code": "hi", "name": "Hindi", "nativeName": "हिन्दी" },
     { "code": "te", "name": "Telugu", "nativeName": "తెలుగు" }
   ]
   ```

---

## 🔄 Trust Score Algorithm

### Trust Score Calculation
```
Initial Score: 50/100

Updates based on:
1. Accepted responses in community (+5 to +15 points)
2. Helpful votes on advice (+1 to +3 points)
3. Positive feedback on suggestions (+2 to +10 points)
4. Negative feedback on suggestions (-5 to -15 points)
5. AI-verified responses (+3 points)
6. Time since joining (gradual increase)
7. Activity level (posts, responses)

Score range: 0-100
Display tiers:
- 0-30: Beginner (gray badge)
- 31-70: Reliable (blue badge)
- 71-100: Expert (gold badge)
```

### Usefulness Score for Suggestions
```
Initial: 50/100

Updates based on:
1. Positive feedback (score 4-5): +10 points
2. Neutral feedback (score 3): +2 points
3. Negative feedback (score 1-2): -10 points
4. Usage frequency: +1 point per use
5. Time decay: -5 points per 6 months

Score affects ranking in suggestion display
```

---

## 📊 Analytics & Reporting Requirements

### User Analytics
- Daily active users
- Disease detection trends
- Most common crops scanned
- Language distribution
- Trust score distribution

### Community Analytics
- Post resolution rate
- Response time metrics
- Most helpful farmers
- Trending diseases/issues
- Geographic hotspots (if location available)

### ML Model Performance
- Prediction accuracy
- False positive/negative rates
- Confidence score distribution
- Model version comparison

---

## 🔔 Notification & Scheduling

### Follow-up System
**Trigger:** User marks suggestion as "Tried this"  
**Action:** Schedule notification for 10-15 days later

**Notification Content:**
```json
{
  "type": "trust_score_followup",
  "title": "How did it work?",
  "message": "Did [Farmer Name]'s suggestion help solve your crop issue?",
  "metadata": {
    "suggestionId": "uuid",
    "scanId": "uuid",
    "farmerName": "string"
  }
}
```

**Implementation Options:**
1. Cron job checking scheduled notifications
2. Queue-based scheduling (Bull/BullMQ with Redis)
3. Cloud scheduler (AWS EventBridge, GCP Cloud Scheduler)

---

## 🚀 Performance Requirements

### Response Time Targets
- Authentication: < 500ms
- Image upload: < 2 seconds
- Disease detection (async): 10-30 seconds
- Community posts fetch: < 300ms
- Search queries: < 500ms

### Scalability
- Support 10,000+ concurrent users
- Handle 50,000+ scans per day
- Store 1M+ community posts
- Process 10,000+ voice recordings per day

### Caching Strategy
- User sessions: Redis (1 hour TTL)
- Community posts: Redis (5 minutes TTL)
- Disease detection results: Database + CDN
- Generated audio: Cloud storage + CDN
- Static translations: In-memory cache

---

## 🛠️ Tech Stack Recommendations

### Backend Framework
- **Node.js:** Express.js / Nest.js / Fastify
- **Python:** FastAPI / Django / Flask
- **Go:** Gin / Echo

### Database
- **Primary:** PostgreSQL (ACID compliance, JSONB support)
- **Cache:** Redis (sessions, rate limiting)
- **File Storage:** AWS S3 / Google Cloud Storage / Azure Blob

### Queue System
- RabbitMQ / Redis Bull / AWS SQS / Google Cloud Tasks

### ML Model Serving
- TensorFlow Serving / TorchServe / FastAPI + Docker

### External APIs
- **Speech Services:** Google Cloud Speech-to-Text
- **Translation:** Google Cloud Translation API
- **Text-to-Speech:** Google Cloud TTS / AWS Polly
- **Image Storage:** AWS S3 / Cloudinary

---

## 📝 Error Handling

### Standard Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "string (ERROR_CODE)",
    "message": "string (user-friendly message)",
    "details": "string (optional technical details)",
    "field": "string (optional field name if validation error)"
  }
}
```

### Common Error Codes
- `AUTH_INVALID_CREDENTIALS`
- `AUTH_TOKEN_EXPIRED`
- `FILE_TOO_LARGE`
- `FILE_INVALID_TYPE`
- `RESOURCE_NOT_FOUND`
- `RATE_LIMIT_EXCEEDED`
- `ML_MODEL_ERROR`
- `VOICE_TRANSCRIPTION_FAILED`
- `VALIDATION_ERROR`

---

## 🧪 Testing Requirements

### Unit Tests
- Authentication logic
- Trust score calculations
- Input validation
- Business logic functions

### Integration Tests
- API endpoint responses
- Database operations
- External API integrations
- File upload flows

### Load Testing
- Concurrent scan submissions
- Community dashboard loads
- Search performance
- ML model throughput

---

## 📦 Deployment Considerations

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Authentication
JWT_SECRET=...
JWT_EXPIRY=24h
REFRESH_TOKEN_EXPIRY=30d

# Cloud Storage
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=...
S3_REGION=...

# Google Cloud APIs
GOOGLE_CLOUD_PROJECT_ID=...
GOOGLE_CLOUD_CREDENTIALS=...

# ML Model
ML_MODEL_ENDPOINT=...
ML_MODEL_API_KEY=...

# Rate Limiting
RATE_LIMIT_WINDOW=60000
RATE_LIMIT_MAX_REQUESTS=100
```

### Docker Considerations
- Multi-stage builds for optimization
- Health check endpoints
- Graceful shutdown handling
- Volume mounting for local development

---

## 🔗 Frontend Integration Points

### Frontend State Management
- **TanStack Query (React Query):** Used for API data fetching and caching
- **React Context:** Language preference, user authentication state
- **LocalStorage:** Auth tokens, language preference

### Frontend Expects
1. **CORS enabled** for development (http://localhost:5173)
2. **JSON responses** for all endpoints
3. **Multipart form data support** for file uploads
4. **Consistent error format** matching the schema above
5. **JWT in Authorization header:** `Bearer <token>`

### API Base URL
Frontend expects base URL to be configurable via environment variable:
```bash
VITE_API_BASE_URL=http://localhost:3000/api
```

---

## 📋 Priority Implementation Order

### Phase 1 (MVP - Week 1-2)
1. ✅ Authentication endpoints (login, register)
2. ✅ User profile management
3. ✅ Basic scan upload and storage
4. ✅ Mock ML response (hardcoded disease detection)
5. ✅ Database schema setup

### Phase 2 (Core Features - Week 3-4)
1. ✅ ML model integration for disease detection
2. ✅ Community posts CRUD operations
3. ✅ Response/comment system
4. ✅ Basic trust score calculation
5. ✅ Image storage in cloud

### Phase 3 (Advanced Features - Week 5-6)
1. ✅ Voice recording transcription
2. ✅ Multi-language translation
3. ✅ Text-to-speech audio generation
4. ✅ AI verification for community responses
5. ✅ Suggestion system with usefulness scores

### Phase 4 (Polish - Week 7-8)
1. ✅ Follow-up notification system
2. ✅ Advanced search and filtering
3. ✅ Analytics dashboard
4. ✅ Performance optimization
5. ✅ Security hardening

---

## 📞 Frontend Contact Points (API Placeholder Functions)

All API integration points are documented in:
**File:** `src/lib/api-placeholders.ts`

**Key Functions:**
1. `onSendForDetection(payload)` - Scan upload
2. `fetchDetectionResult(scanId)` - Get detection result
3. `playTranslatedMessage(scanId, language)` - TTS audio
4. `fetchSuggestions(scanId)` - Get suggestions
5. `submitTrustScore(suggestionId, score)` - Submit feedback
6. `shareToCommunity(prefill)` - Share to community
7. `openNewPostWithPrefill(prefill)` - New community post

---

## 🎨 UI/UX Considerations for Backend

### Disease Reliability Color Coding
Backend should ensure reliability scores align with frontend display:
- **High (76-100):** Green - Confident detection
- **Medium (51-75):** Yellow - Moderate confidence
- **Medium-Low (26-50):** Orange - Low confidence, suggest community input
- **Low (0-25):** Red - Very uncertain, recommend community verification

### Trust Score Badge Tiers
Backend calculations should result in these tiers:
- **Beginner (0-30):** Gray badge
- **Reliable (31-70):** Blue badge  
- **Expert (71-100):** Gold badge

---

## 📚 Additional Notes

### Crop Information Database
Frontend has a **Documentation page** with 10 major crops:
- Ragi, Sunflower, Groundnut, Cotton, Sugarcane, Turmeric, Pulses, Grapes, Chilli, Rice

Backend should consider:
- Storing crop-specific disease databases
- Seasonal information for better context
- Common information gaps farmers face

### Community Workflow
1. **Common Disease:** AI detection → Show suggestions + community advice
2. **Rare Disease:** AI detection → Prompt user to post on community dashboard
3. **Community Response:** User posts → Other farmers respond → AI verifies responses
4. **Follow-up:** User tries suggestion → Backend schedules follow-up → User provides feedback → Trust scores update

---

## 🎯 Success Metrics

Backend should track:
1. **Detection accuracy:** % of correctly identified diseases
2. **Community engagement:** Posts, responses, resolution rate
3. **Trust score reliability:** Correlation with actual helpful advice
4. **Response time:** API performance metrics
5. **User retention:** Active users over time
6. **Language usage:** Distribution across languages

---

## 🔍 Special Features to Implement

### 1. Government Extension Worker Verification
- Special role for government agriculture officers
- Verified badge on their responses
- Higher weight in trust score calculations
- Priority notification for rare diseases

### 2. Trending Disease Alerts
- Track disease outbreaks by region
- Send notifications to farmers in affected areas
- Display trending issues on dashboard

### 3. Offline Support (Future)
- Cache common disease data
- Queue scans for later upload
- Progressive Web App support

---

## 📖 API Documentation Requirements

Backend should provide:
1. **OpenAPI/Swagger documentation**
2. **Postman collection** for testing
3. **Authentication flow diagrams**
4. **Rate limiting details**
5. **Webhook documentation** (if implemented)
6. **Error code reference**

---

## ✅ Conclusion

This comprehensive report provides everything needed to build a robust backend for KrishiLok. The platform combines cutting-edge AI with community-driven knowledge to empower farmers across India.

**Key Success Factors:**
- Fast and accurate disease detection
- Reliable community trust system
- Seamless multi-language support
- Scalable architecture
- Excellent user experience through optimized APIs

**Questions or clarifications?** All frontend API integration points are clearly marked in `src/lib/api-placeholders.ts` with detailed comments.

---

**Report Generated:** 2025-10-25  
**Frontend Framework:** React 18 + TypeScript + Vite  
**Package Manager:** Bun  
**Ready for Backend Development:** ✅
