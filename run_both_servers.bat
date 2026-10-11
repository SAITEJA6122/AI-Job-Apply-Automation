@echo off
echo ========================================
echo   Starting Naukri Job Automation
echo ========================================
echo.

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
    echo ERROR: Virtual environment not found!
    echo Please run install_dependencies.bat first.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

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
echo Open your browser to: http://localhost:3000
echo.
echo Two terminal windows have opened:
echo   1. Backend Server (Flask) - Keep this open
echo   2. Frontend Server (React) - Keep this open
echo.
echo Close those windows to stop the servers.
echo.
pause
