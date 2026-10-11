@echo off
echo ========================================
echo   Starting Naukri Job Automation
echo ========================================
echo.

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

echo Starting Backend (Flask)...
start "Backend Server" cmd /k ".venv\Scripts\activate.bat && python backend\app.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo Starting Frontend (React)...
start "Frontend Server" cmd /k "cd frontend && yarn dev"

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
echo Press any key to close this window (servers will continue running)...
pause >nul
