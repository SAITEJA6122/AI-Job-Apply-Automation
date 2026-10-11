# Naukri Job Automation - Production-Ready Frontend Setup

Complete setup guide for the production-ready Naukri Job Automation system with modern web dashboard.

## Overview

This system provides:
- **Automated Job Applications**: Uses Playwright to apply to jobs on Naukri
- **Modern Web Dashboard**: React + TypeScript frontend with real-time updates
- **Secure Session Management**: 24-hour automatic session deletion
- **No Password Storage**: Session-based authentication only
- **Resume Parsing**: Automatic extraction of resume data
- **Profile Management**: Complete profile configuration
- **AI-Powered Responses**: Gemini/Groq integration for screening questions

## Architecture

```
┌─────────────────────┐
│   Web Dashboard      │
│   (React + TS)       │
│   Port: 3000         │
└──────────┬──────────┘
           │
           │ REST API
           │
┌──────────▼──────────┐
│   Backend API        │
│   (Flask + SQLite)  │
│   Port: 5000        │
└──────────┬──────────┘
           │
           │ profile.yaml
           │ session_naukri.json
           │
┌──────────▼──────────┐
│   Python Automation │
│   (Playwright)      │
└──────────┬──────────┘
           │
           │ Browser
           │
┌──────────▼──────────┐
│   Naukri Website    │
└─────────────────────┘
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- Git
- Chromium browser (installed by Playwright)

## Installation

### 1. Clone the Repository

```bash
cd naukri-job-apply-ai-main
```

### 2. Python Backend Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 3. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
# GEMINI_API_KEY=your-gemini-key
# GROQ_API_KEY=your-groq-key (optional)
```

### 4. Configure Profile

```bash
# Copy example profile
cp profile.example.yaml profile.yaml

# Edit profile.yaml with your details
# target_roles, experience, locations, skills, etc.
```

### 5. Frontend Setup

```bash
cd frontend

# Install Node.js dependencies
npm install

# Return to project root
cd ..
```

## Running the Application

### Option 1: Development Mode (Recommended for Testing)

**Terminal 1 - Start Backend:**
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Start backend
python backend/app.py
```

Backend will run on `http://localhost:5000`

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm run dev
```

Frontend will run on `http://localhost:3000`

### Option 2: Production Mode

**Start Backend:**
```bash
# Activate virtual environment
.venv\Scripts\activate

# Start with gunicorn (install first: pip install gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

**Build and Start Frontend:**
```bash
cd frontend

# Build for production
npm run build

# Preview production build
npm run preview
```

## First-Time Setup

### 1. Connect Naukri Account

1. Open web dashboard: `http://localhost:3000`
2. Navigate to Dashboard
3. Click "Connect Naukri"
4. Browser window will open
5. Log in to Naukri manually (password, OTP, CAPTCHA)
6. Return to terminal and press Enter
7. Session will be saved and connected

**Important**: Password is never stored. Only session cookies are saved.

### 2. Upload Resume

1. Navigate to Resume page
2. Drag and drop your resume (PDF, DOC, DOCX)
3. System will automatically parse and extract data
4. Review extracted information
5. Edit if necessary
6. Click "Approve & Save"
7. Data will sync with profile.yaml

### 3. Configure Profile

1. Navigate to Profile page
2. Fill in personal information
3. Add professional details
4. Add skills
5. Save profile

### 4. Configure Job Preferences

1. Navigate to Job Preferences page
2. Select target roles
3. Set experience range
4. Configure location preferences
5. Set salary expectations
6. Save preferences

### 5. Start Automation

1. Navigate to Dashboard
2. Ensure Naukri is connected
3. Click "Start Automation"
4. Monitor progress in real-time
5. View application history in Applications page

## Security Features

### 24-Hour Session Deletion

All temporary data is automatically deleted after 12 hours:
- Naukri session cookies
- Browser profiles
- Temporary resume files
- Database session records

Cleanup runs:
- Every hour (background worker)
- On application startup
- Manually via Settings page

### No Password Storage

- Naukri passwords are never stored
- Authentication is session-based only
- User logs in manually in browser
- Session cookies are captured and reused

### Secure File Storage

- Resume files stored in protected directory
- Files deleted after 12 hours
- No public access to session files

## API Endpoints

### Session Management
- `GET /api/session/status` - Get session status
- `POST /api/naukri/connect` - Connect Naukri
- `POST /api/naukri/disconnect` - Disconnect Naukri

### Profile Management
- `GET /api/profile` - Get profile
- `POST /api/profile` - Update profile

### Resume Management
- `POST /api/resume/upload` - Upload resume
- `POST /api/resume/approve` - Approve parsed data

### Automation Control
- `POST /api/automation/start` - Start automation
- `POST /api/automation/stop` - Stop automation
- `GET /api/automation/status` - Get status

## Troubleshooting

### Backend Not Starting

**Issue**: Port 5000 already in use
```bash
# Windows: Find and kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill -9
```

### Frontend Not Starting

**Issue**: Port 3000 already in use
```bash
# Change port in vite.config.ts
server: {
  port: 3001,  // Change to available port
}
```

### Session Not Connecting

**Issue**: Playwright browser not launching
```bash
# Reinstall Playwright browsers
playwright install chromium --force
```

### Resume Parsing Failed

**Issue**: Missing dependencies
```bash
# Install python-docx for DOCX support
pip install python-docx
```

### Automation Not Starting

**Issue**: profile.yaml missing or invalid
```bash
# Ensure profile.yaml exists
cp profile.example.yaml profile.yaml

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('profile.yaml'))"
```

## Database Management

### View Database

```bash
# Using SQLite command line
sqlite3 backend/sessions.db

# List tables
.tables

# View sessions
SELECT * FROM naukri_sessions;

# Exit
.quit
```

### Reset Database

```bash
# Delete database file
rm backend/sessions.db

# Restart backend (will recreate database)
python backend/app.py
```

## Logs

### Backend Logs
- Console output in terminal
- For production, configure file logging

### Automation Logs
- `applications_log.csv` - Application history
- `application_stats.json` - Statistics
- `security_events.jsonl` - Security events

## Deployment

### Production Deployment Checklist

- [ ] Use HTTPS
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set up proper logging
- [ ] Configure environment variables
- [ ] Use production WSGI server (gunicorn)
- [ ] Set up process manager (systemd/supervisor)
- [ ] Configure firewall rules
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Use production API keys (not free tier)

### Docker Deployment (Optional)

Create `Dockerfile` for backend:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:app"]
```

Create `Dockerfile` for frontend:
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "run", "preview"]
```

## Maintenance

### Regular Tasks

1. **Monitor Session Cleanup**: Ensure cleanup worker is running
2. **Review Application Logs**: Check for errors or issues
3. **Update Dependencies**: Keep packages up to date
4. **Backup Database**: Regular database backups
5. **Monitor Disk Space**: Temporary files should be cleaned automatically

### Update Automation

```bash
# Pull latest changes
git pull

# Update Python dependencies
pip install -r requirements.txt --upgrade

# Update Node dependencies
cd frontend
npm update
cd ..

# Restart services
```

## Support

For issues or questions:
1. Check backend/README.md for API documentation
2. Check frontend/README.md for frontend documentation
3. Review logs for error messages
4. Check existing issues in repository

## License

MIT License - See LICENSE file for details

## Disclaimer

This tool automates actions against Naukri's terms of service. Use at your own discretion. The project includes safety features but cannot eliminate all risks. Users are responsible for:
- Compliance with Naukri's terms of service
- Account security and consequences
- Reviewing and understanding all code before use
