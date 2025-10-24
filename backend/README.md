# KrishiLok Backend API

> Agricultural Community Support Platform with AI-powered disease detection

## 🌾 Features

- **JWT Authentication** - Secure user registration and login
- **Disease Detection** - Crop image upload and disease identification
- **Community Forum** - Posts, comments, and knowledge sharing
- **Trust Score System** - Community-driven reputation system
- **Suggestions** - Crowdsourced farming advice
- **Notifications** - User notification system
- **File Upload** - Image storage for scans and posts

## 📋 Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT with python-jose
- **Password Hashing**: Bcrypt (passlib)
- **File Handling**: aiofiles
- **CORS**: Enabled for frontend integration

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- MongoDB installed and running
- pip (Python package manager)

### Installation

1. **Clone the repository** (if not already done)
   ```bash
   cd backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   
   Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   
   Copy `.env.example` to `.env` and update values:
   ```bash
   copy .env.example .env
   ```
   
   Update `SECRET_KEY` in `.env` with a secure random key:
   ```
   SECRET_KEY=your-secure-secret-key-here
   ```

6. **Start MongoDB**
   
   Make sure MongoDB is running on `mongodb://localhost:27017`
   
   Windows:
   ```bash
   mongod
   ```
   
   Linux/Mac:
   ```bash
   sudo systemctl start mongod
   ```

7. **Run the server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   
   Or use Python directly:
   ```bash
   python -m app.main
   ```

## 📡 API Endpoints

### Base URL
```
http://localhost:8000/api
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "farmer@example.com",
  "password": "password123",
  "name": "Ramesh Kumar",
  "phone": "9876543210",
  "language": "en"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "identifier": "farmer@example.com",
  "password": "password123",
  "language": "en"
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>
```

### Disease Detection Endpoints

#### Upload Scan
```http
POST /api/scans
Content-Type: multipart/form-data
Authorization: Bearer <token>

image: [file]
crop_name: "Tomato"
description: "Yellow spots on leaves"
language: "en"
```

#### Get User Scans
```http
GET /api/scans?skip=0&limit=10
Authorization: Bearer <token>
```

#### Get Scan Details
```http
GET /api/scans/{scan_id}
Authorization: Bearer <token>
```

### Community Endpoints

#### Create Post
```http
POST /api/community/posts
Content-Type: multipart/form-data
Authorization: Bearer <token>

title: "Help with tomato disease"
description: "My plants are yellowing..."
crop_name: "Tomato"
tags: "disease,help"
language: "en"
image: [optional file]
```

#### Get Posts
```http
GET /api/community/posts?page=1&limit=10&status_filter=unresolved
```

#### Get Post Details
```http
GET /api/community/posts/{post_id}
```

#### Add Comment
```http
POST /api/community/posts/{post_id}/respond
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "Try using neem oil spray...",
  "is_expert_advice": false
}
```

#### Resolve Post
```http
POST /api/community/posts/{post_id}/resolve
Authorization: Bearer <token>
Content-Type: application/json

{
  "accepted_response_id": "response_123"
}
```

### Suggestions Endpoints

#### Get Suggestions
```http
GET /api/suggestions/{scan_id}
Authorization: Bearer <token>
```

#### Submit Trust Feedback
```http
POST /api/suggestions/trust-score
Authorization: Bearer <token>
Content-Type: application/json

{
  "suggestion_id": "suggestion_123",
  "score": 5,
  "feedback": "This worked perfectly!",
  "scan_id": "scan_123"
}
```

### Notifications Endpoints

#### Get Notifications
```http
GET /api/notifications?unread_only=true&limit=20
Authorization: Bearer <token>
```

#### Mark as Read
```http
PATCH /api/notifications/{notification_id}/read
Authorization: Bearer <token>
```

## 🗄️ Database Collections

The MongoDB database (`krishilok_db`) contains the following collections:

- **users** - User accounts and authentication
- **scans** - Disease detection scans
- **community_posts** - Community forum posts
- **post_comments** - Comments on posts
- **suggestions** - Community suggestions
- **trust_feedback** - Trust score feedback
- **notifications** - User notifications

Collections are created automatically on first use.

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. Register or login to receive a JWT token
2. Include token in Authorization header for protected endpoints:
   ```
   Authorization: Bearer <your-token-here>
   ```
3. Tokens expire after 7 days (configurable in `.env`)

## 📁 File Uploads

- Uploaded files are stored in `./uploads/` directory
- Supported formats: JPG, JPEG, PNG, WEBP
- Maximum file size: 10MB
- Files are organized in subfolders:
  - `uploads/scans/` - Crop scan images
  - `uploads/posts/` - Community post images
  - `uploads/avatars/` - User avatars

## 🧪 Testing the API

### Using Swagger UI (Recommended)

1. Start the server
2. Open http://localhost:8000/docs
3. Click "Authorize" and enter your JWT token
4. Try out different endpoints

### Using curl

Register a user:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"test123\",\"name\":\"Test User\"}"
```

Login:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"identifier\":\"test@example.com\",\"password\":\"test123\"}"
```

### Testing Checklist

- [ ] Server starts without errors
- [ ] `/health` endpoint returns 200
- [ ] Can register a new user
- [ ] Can login and receive JWT token
- [ ] Protected endpoints reject requests without token
- [ ] Can upload image and create scan
- [ ] Can create community post
- [ ] MongoDB collections are created automatically

## 🛠️ Development

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Environment configuration
│   ├── database.py          # MongoDB connection
│   ├── models/              # Pydantic models
│   │   ├── user.py
│   │   ├── scan.py
│   │   ├── community.py
│   │   ├── suggestion.py
│   │   └── notification.py
│   ├── routes/              # API endpoints
│   │   ├── auth.py
│   │   ├── scans.py
│   │   ├── community.py
│   │   ├── suggestions.py
│   │   └── notifications.py
│   ├── services/            # Business logic
│   │   ├── auth_service.py
│   │   ├── storage_service.py
│   │   └── trust_score.py
│   └── utils/
│       ├── security.py      # JWT & password hashing
│       └── dependencies.py  # Auth dependencies
├── uploads/                 # File storage
├── requirements.txt
├── .env                     # Environment variables
└── README.md
```

### Adding New Features

1. **Create model** in `app/models/`
2. **Add service logic** in `app/services/`
3. **Create routes** in `app/routes/`
4. **Include router** in `app/main.py`

### Trust Score Algorithm

The trust score system (0-100) adjusts based on:

- **+10 points**: Accepted response in community
- **+3 points**: AI-verified response
- **+5 points**: Positive feedback (score 4-5)
- **+2 points**: Helpful vote
- **-5 points**: Negative feedback (score 1-2)
- **-10 points**: Reported content

Base score: 50

## 🚧 TODO / Future Enhancements

- [ ] Integrate actual ML model for disease detection
- [ ] Add voice transcription service
- [ ] Implement text-to-speech for results
- [ ] Add AI verification for community responses
- [ ] Set up Redis for caching
- [ ] Add rate limiting
- [ ] Implement email notifications
- [ ] Add comprehensive logging
- [ ] Set up automated tests
- [ ] Deploy to production server

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `DATABASE_NAME` | Database name | `krishilok_db` |
| `SECRET_KEY` | JWT secret key | (required) |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_DAYS` | Token expiry in days | `7` |
| `UPLOAD_FOLDER` | File upload directory | `./uploads` |
| `MAX_UPLOAD_SIZE` | Max file size in bytes | `10485760` (10MB) |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:5173` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |

## 🐛 Troubleshooting

### MongoDB Connection Failed
- Ensure MongoDB is running: `mongod`
- Check connection string in `.env`
- Verify port 27017 is not blocked

### Import Errors
- Activate virtual environment
- Install all dependencies: `pip install -r requirements.txt`

### CORS Errors
- Check `FRONTEND_URL` in `.env`
- Verify CORS middleware configuration in `main.py`

### File Upload Errors
- Check `uploads/` directory exists and is writable
- Verify file size is under 10MB
- Ensure file type is JPG/PNG/WEBP

## 📄 License

MIT License - Feel free to use this project for learning and development.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the `/docs` endpoint for API documentation
- Review error messages in server logs
- Verify environment configuration

---

**Built with ❤️ for farmers by the KrishiLok team**
