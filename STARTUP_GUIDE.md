# KrishiLok - Complete Startup Guide

## 🚀 Quick Start (All Services)

### Prerequisites Checklist
- [ ] Python 3.9+ installed
- [ ] Node.js 16+ installed  
- [ ] MongoDB installed
- [ ] Git installed

---

## 📦 Step 1: MongoDB Setup

### Start MongoDB on Port 27018

**Windows:**
```powershell
# Create data directory
mkdir C:\data\db27018

# Start MongoDB
mongod --port 27018 --dbpath "C:\data\db27018"
```

**Keep this terminal open!**

---

## 🔧 Step 2: Backend Setup

**Open a NEW terminal:**

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify .env file exists and has correct settings
# Should have: MONGODB_URI=mongodb://localhost:27018

# Start backend server
uvicorn app.main:app --reload --port 8000
```

**Keep this terminal open!**

**Backend will run on:** http://localhost:8000
**API Documentation:** http://localhost:8000/docs

---

## 🎨 Step 3: Frontend Setup

**Open a NEW terminal:**

```powershell
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Keep this terminal open!**

**Frontend will run on:** http://localhost:5173

---

## ✅ Step 4: Verify Everything Works

### Test Checklist

1. **MongoDB Health Check**
   - Open: http://localhost:8000/health
   - Should return: `{"status": "healthy", "database": "connected"}`

2. **API Documentation**
   - Open: http://localhost:8000/docs
   - You should see Swagger UI with all endpoints

3. **Frontend**
   - Open: http://localhost:5173
   - You should see the KrishiLok homepage

4. **Test Signup**
   - Go to: http://localhost:5173/signup
   - Fill in the form:
     - Name: Test Farmer
     - Email: test@example.com
     - Password: test123
   - Click "Sign Up"
   - Should see success message

5. **Test Login**
   - Go to: http://localhost:5173/login
   - Enter:
     - Identifier: test@example.com
     - Password: test123
   - Click "Sign In"
   - Should redirect to dashboard

---

## 🛠️ Common Issues & Solutions

### Issue 1: MongoDB Connection Error
**Error:** `Connection refused` or `MongoServerError`

**Solution:**
```powershell
# Check if MongoDB is running on port 27018
netstat -an | findstr :27018

# If not running, start it:
mongod --port 27018 --dbpath "C:\data\db27018"
```

### Issue 2: Backend Import Errors
**Error:** `ModuleNotFoundError` or `ImportError`

**Solution:**
```powershell
# Make sure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 3: Frontend Not Loading
**Error:** `VITE_API_URL not defined` or API errors

**Solution:**
```powershell
# Check .env file exists
ls .env

# Should contain:
# VITE_API_URL=http://localhost:8000/api

# Restart frontend server
npm run dev
```

### Issue 4: CORS Errors
**Error:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution:**
- Backend should already have CORS enabled
- Restart backend server
- Make sure frontend is on http://localhost:5173

### Issue 5: Port Already in Use

**For Backend (8000):**
```powershell
# Use different port
uvicorn app.main:app --reload --port 8001

# Update frontend .env
VITE_API_URL=http://localhost:8001/api
```

**For Frontend (5173):**
```powershell
# Vite will auto-assign next available port
# Or specify: npm run dev -- --port 5174
```

**For MongoDB (27018):**
```powershell
# Use port 27019
mongod --port 27019 --dbpath "C:\data\db27019"

# Update backend .env
MONGODB_URI=mongodb://localhost:27019
```

---

## 🔄 Daily Development Workflow

**Starting Work:**
```powershell
# Terminal 1: MongoDB
mongod --port 27018 --dbpath "C:\data\db27018"

# Terminal 2: Backend
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Terminal 3: Frontend
cd frontend
npm run dev
```

**Stopping Work:**
- Press `Ctrl+C` in each terminal
- Or close all terminal windows

---

## 📊 Service Status Dashboard

Open these URLs to verify services:

| Service | URL | Status Check |
|---------|-----|--------------|
| **Frontend** | http://localhost:5173 | Should show homepage |
| **Backend API** | http://localhost:8000/docs | Should show Swagger UI |
| **Health Check** | http://localhost:8000/health | Should return JSON |
| **MongoDB** | mongosh --port 27018 | Should connect |

---

## 🧪 Testing the Full Flow

### 1. Create Account
1. Go to http://localhost:5173/signup
2. Enter details and sign up
3. Should see success message

### 2. Login
1. Go to http://localhost:5173/login
2. Enter credentials
3. Should redirect to dashboard

### 3. Upload Crop Image
1. From dashboard, go to "Scan Crop"
2. Upload an image
3. Fill in crop details
4. Submit
5. Should see detection results

### 4. Community Post
1. Go to "Community" section
2. Create a new post
3. Should see it in the feed

---

## 📝 Environment Variables Reference

### Backend (.env)
```env
MONGODB_URI=mongodb://localhost:27018
DATABASE_NAME=krishilok_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=7
UPLOAD_FOLDER=./uploads
MAX_UPLOAD_SIZE=10485760
FRONTEND_URL=http://localhost:5173
HOST=0.0.0.0
PORT=8000
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api
```

---

## 🔐 Security Notes

### For Development:
- ✅ Current SECRET_KEY is fine
- ✅ CORS allows all origins
- ✅ No HTTPS required

### For Production:
- ⚠️ Change SECRET_KEY to random 32+ character string
- ⚠️ Restrict CORS to specific domains
- ⚠️ Enable HTTPS
- ⚠️ Use environment variables, not .env files
- ⚠️ Set up MongoDB authentication

---

## 📚 Additional Resources

- **Backend API Docs:** http://localhost:8000/docs
- **Backend README:** `backend/README.md`
- **MongoDB Setup:** `MONGODB_SETUP.md`
- **Frontend Package:** `frontend/package.json`

---

## 🆘 Still Having Issues?

1. Check all three services are running
2. Verify ports are correct
3. Check `.env` files exist
4. Try restarting all services
5. Check terminal for error messages
6. Verify Python/Node versions

---

## 🎯 Success Criteria

You're ready to develop when:
- ✅ MongoDB connects successfully
- ✅ Backend /health returns healthy status
- ✅ Frontend loads without errors
- ✅ Can sign up new user
- ✅ Can login with credentials
- ✅ API calls work from frontend to backend

**Happy Coding! 🌾**
