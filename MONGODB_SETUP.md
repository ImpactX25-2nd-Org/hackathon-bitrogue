# MongoDB Setup on Custom Port (27018)

## Starting MongoDB on Port 27018

Since the default port 27017 is already in use, we'll run MongoDB on port 27018.

### Windows

#### Option 1: Using Command Line (One-time)
```powershell
mongod --port 27018 --dbpath "C:\data\db27018"
```

#### Option 2: Using Configuration File (Recommended)

1. **Create a config file** `C:\mongodb\mongod-27018.cfg`:
```yaml
systemLog:
  destination: file
  path: C:\mongodb\logs\mongod-27018.log
  logAppend: true

storage:
  dbPath: C:\mongodb\data\db27018

net:
  port: 27018
  bindIp: 127.0.0.1
```

2. **Create the data directory:**
```powershell
mkdir C:\mongodb\data\db27018
mkdir C:\mongodb\logs
```

3. **Start MongoDB with the config:**
```powershell
mongod --config C:\mongodb\mongod-27018.cfg
```

#### Option 3: Install as Windows Service (Best for Development)

1. **Create data directories:**
```powershell
mkdir C:\mongodb\data\db27018
mkdir C:\mongodb\logs
```

2. **Install MongoDB service:**
```powershell
mongod --config C:\mongodb\mongod-27018.cfg --install --serviceName "MongoDB27018" --serviceDisplayName "MongoDB on Port 27018"
```

3. **Start the service:**
```powershell
net start MongoDB27018
```

4. **Stop the service:**
```powershell
net stop MongoDB27018
```

5. **Remove the service (if needed):**
```powershell
mongod --remove --serviceName "MongoDB27018"
```

### Linux/Mac

#### Option 1: Using Command Line
```bash
mongod --port 27018 --dbpath ~/data/db27018
```

#### Option 2: Using Configuration File

1. **Create config file** `~/mongodb/mongod-27018.conf`:
```yaml
systemLog:
  destination: file
  path: ~/mongodb/logs/mongod-27018.log
  logAppend: true

storage:
  dbPath: ~/mongodb/data/db27018

net:
  port: 27018
  bindIp: 127.0.0.1
```

2. **Create directories:**
```bash
mkdir -p ~/mongodb/data/db27018
mkdir -p ~/mongodb/logs
```

3. **Start MongoDB:**
```bash
mongod --config ~/mongodb/mongod-27018.conf
```

## Verify MongoDB is Running

```powershell
# Test connection
mongosh --port 27018

# Or check if port is listening
netstat -an | findstr :27018
```

## Connect to MongoDB

```javascript
// MongoDB Connection String
mongodb://localhost:27018

// Using mongosh
mongosh "mongodb://localhost:27018"
```

## Backend Configuration

The backend `.env` file is already configured to use port 27018:

```env
MONGODB_URI=mongodb://localhost:27018
DATABASE_NAME=krishilok_db
```

## Troubleshooting

### Port Already in Use
If port 27018 is also in use, change to another port:
1. Update `.env`: `MONGODB_URI=mongodb://localhost:27019`
2. Start MongoDB: `mongod --port 27019 --dbpath "C:\data\db27019"`

### Connection Refused
- Ensure MongoDB is running
- Check firewall settings
- Verify the port number matches in both MongoDB and `.env`

### Data Directory Error
- Create the directory first: `mkdir C:\mongodb\data\db27018`
- Or use existing directory with `--dbpath` flag

## Quick Start Commands

**Windows (PowerShell):**
```powershell
# Simple start
mongod --port 27018 --dbpath "C:\data\db27018"

# In a new terminal, start backend
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# In another terminal, start frontend
cd frontend
npm run dev
```

**Linux/Mac:**
```bash
# Simple start
mongod --port 27018 --dbpath ~/data/db27018

# In a new terminal, start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# In another terminal, start frontend
cd frontend
npm run dev
```
