@echo off
echo ========================================
echo   Setup and Run Naukri Job Automation
echo ========================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Check if .env exists
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env >nul
    echo Please edit .env and add your API keys before running automation
    echo.
)

REM Check if profile.yaml exists
if not exist profile.yaml (
    echo Creating profile.yaml from profile.example.yaml...
    copy profile.example.yaml profile.yaml >nul
    echo Please edit profile.yaml with your details
    echo.
)

REM Check if virtual environment exists
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install backend dependencies
echo Installing backend dependencies...
pip install -r requirements.txt
echo.

REM Install new dependencies for enhancements
echo Installing additional dependencies...
pip install flask-socketio python-socketio cryptography pytest pytest-flask
echo.

REM Check if frontend node_modules exists
if not exist frontend\node_modules (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    call npm install socket.io-client
    cd ..
    echo.
) else (
    echo Installing new frontend dependency...
    cd frontend
    call npm install socket.io-client
    cd ..
    echo.
)

echo ========================================
echo   Starting Servers
echo ========================================
echo.

REM Start Backend (Flask)
echo Starting Backend (Flask) on port 5000...
start "Backend Server" cmd /k "cd /d %~dp0 && .venv\Scripts\activate.bat && python backend\app.py"

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start Frontend (React)
echo Starting Frontend (React) on port 3000...
start "Frontend Server" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo   Servers started successfully!
echo ========================================
echo.
echo Backend URL: http://127.0.0.1:5000
echo Frontend URL: http://localhost:3000
echo.
echo Open your browser to http://localhost:3000
echo.
echo Note: Two new terminal windows have opened:
echo   - Backend Server (Flask)
echo   - Frontend Server (React/Vite)
echo.
echo Close those windows to stop the servers.
echo.
pause
