# Quick Start Guide - Naukri Job Apply AI

## Step-by-Step Instructions to Run the Project

### Prerequisites

Before running the project, ensure you have:
- **Python 3.8+** installed
- **Node.js 16+** installed
- **npm** or **yarn** installed

---

## Method 1: One-Command Setup and Run (Recommended)

### For PowerShell Users:

```powershell
.\setup_and_run.ps1
```

### For Command Prompt (cmd) Users:

**Double-click** `setup_and_run.bat`

Or run in cmd:
```batch
setup_and_run.bat
```

These scripts will:
- ✅ Create virtual environment (if not exists)
- ✅ Install all Python dependencies
- ✅ Install all Node.js dependencies
- ✅ Start both Backend and Frontend servers
- ✅ Open browser at http://localhost:3000

**That's it!** The project will be running in two separate terminal windows.

---

## Method 2: Two-Step Process

### Step 1: Install Dependencies

**PowerShell:**
```powershell
.\install_dependencies.ps1
```

**Command Prompt:**
```batch
install_dependencies.bat
```

This will:
- Create Python virtual environment
- Install all backend dependencies (Flask, WebSocket, SSL, Testing)
- Install all frontend dependencies (React, Socket.io, etc.)

### Step 2: Run Servers

**PowerShell:**
```powershell
.\run_both_servers.ps1
```

**Command Prompt:**
```batch
run_both_servers.bat
```

This will:
- Start Backend server on http://127.0.0.1:5000
- Start Frontend server on http://localhost:3000
- Open two terminal windows for monitoring

---

## Method 3: Manual Setup (If Scripts Fail)

### Step 1: Setup Python Environment

```batch
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install flask-socketio python-socketio cryptography pytest pytest-flask
```

### Step 2: Setup Frontend

```batch
cd frontend
npm install
npm install socket.io-client
cd ..
```

### Step 3: Configure Environment

```batch
# Copy example .env file
copy .env.example .env

# Copy example profile
copy profile.example.yaml profile.yaml
```

Edit `.env` and add your API keys if needed.

### Step 4: Run Backend

```batch
# In one terminal
.venv\Scripts\activate
python backend\app.py
```

Backend will run on: http://127.0.0.1:5000

### Step 5: Run Frontend

```batch
# In another terminal
cd frontend
npm run dev
```

Frontend will run on: http://localhost:3000

---

## Accessing the Application

Once both servers are running:

1. Open your browser
2. Go to: **http://localhost:3000**
3. You will see the Naukri Job Automation Dashboard

---

## Server URLs

- **Frontend (React):** http://localhost:3000
- **Backend (Flask API):** http://127.0.0.1:5000
- **API Health Check:** http://127.0.0.1:5000/api/health

---

## Stopping the Servers

To stop the servers:
1. Close the Backend terminal window
2. Close the Frontend terminal window
3. Or press `Ctrl+C` in each terminal

---

## Troubleshooting

### Python/pip Path Issues

If you see "Unable to create process" error:

**Solution:**
```batch
# Use python -m pip instead of pip
python -m pip install -r requirements.txt
```

### Port Already in Use

If port 5000 or 3000 is already in use:

**Solution:**
- Close other applications using those ports
- Or modify the port in:
  - Backend: `backend/app.py` (change port=5000)
  - Frontend: `frontend/vite.config.ts` (change port)

### Virtual Environment Issues

If virtual environment activation fails:

**Solution:**
```batch
# Delete and recreate
rmdir /s .venv
python -m venv .venv
.venv\Scripts\activate
```

### Node Modules Issues

If frontend dependencies fail:

**Solution:**
```batch
cd frontend
rmdir /s node_modules
del package-lock.json
npm install
```

---

## Running Tests

After installation, run tests:

```batch
.venv\Scripts\activate
pytest tests/ -v
```

---

## Enabling HTTPS (Optional)

To run with HTTPS (development only):

**Windows:**
```batch
set ENABLE_HTTPS=true
.venv\Scripts\activate
python backend/app.py
```

**PowerShell:**
```powershell
$env:ENABLE_HTTPS="true"
python backend\app.py
```

---

## Docker Alternative (If Available)

If you have Docker installed:

```batch
docker-compose up
```

This will:
- Build and start Backend container
- Build and start Frontend container
- Run both services simultaneously

---

## File Structure

```
naukri-job-apply-ai-main/
├── backend/              # Flask Backend
│   └── app.py           # Main backend server
├── frontend/            # React Frontend
│   ├── src/            # React source code
│   └── package.json    # Frontend dependencies
├── common/             # Shared utilities
├── tests/              # Unit tests
├── .venv/              # Python virtual environment
├── .env                # Environment variables
├── profile.yaml        # User profile configuration
├── requirements.txt    # Python dependencies
├── setup_and_run.bat   # One-command setup & run ⭐
├── install_dependencies.bat  # Install dependencies only
└── run_both_servers.bat     # Run servers only
```

---

## New Features Available

After installation, these features are available:

✅ **Dark Mode** - Toggle in sidebar
✅ **Real-Time Progress** - WebSocket-based progress updates
✅ **Terminal Output** - Live automation logs
✅ **Pagination** - For application history
✅ **Job Matching** - Score-based job recommendations
✅ **Better Error Handling** - User-friendly error messages
✅ **Unit Tests** - pytest test suite
✅ **HTTPS Support** - SSL certificates (development)

---

## Support

If you encounter issues:

1. Check the terminal windows for error messages
2. Ensure all dependencies are installed
3. Verify Python and Node.js are correctly installed
4. Check that ports 5000 and 3000 are available

---

## Next Steps

1. **Edit `.env`** - Add your API keys if needed
2. **Edit `profile.yaml`** - Add your job preferences
3. **Open http://localhost:3000** - Start using the application
4. **Connect Naukri** - Login via the Dashboard
5. **Start Automation** - Begin automated job applications

---

**Happy Automating! 🚀**
