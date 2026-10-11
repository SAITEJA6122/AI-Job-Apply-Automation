@echo off
echo ========================================
echo   Installing Dependencies
echo ========================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        echo Please ensure Python is installed and accessible.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install backend dependencies
echo Installing backend dependencies from requirements.txt...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies.
    pause
    exit /b 1
)
echo.

REM Install new dependencies for enhancements
echo Installing additional dependencies (WebSocket, SSL, Testing)...
python -m pip install flask-socketio python-socketio cryptography pytest pytest-flask
if errorlevel 1 (
    echo WARNING: Some additional dependencies failed to install.
    echo The project may still work, but some features will be unavailable.
    echo.
)
echo.

REM Install frontend dependencies
echo Installing frontend dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies.
    cd ..
    pause
    exit /b 1
)
echo.

REM Install socket.io-client for frontend
echo Installing socket.io-client for WebSocket support...
call npm install socket.io-client
if errorlevel 1 (
    echo WARNING: socket.io-client installation failed.
    echo Real-time progress features may not work.
    echo.
)
cd ..

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo All dependencies have been installed successfully.
echo You can now run the project using:
echo   - run_both_servers.bat
echo   - Or run start_project.bat
echo.
pause
