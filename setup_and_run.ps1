# PowerShell Setup and Run Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup and Run Naukri Job Automation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Please edit .env and add your API keys before running automation" -ForegroundColor Yellow
    Write-Host ""
}

# Check if profile.yaml exists
if (-not (Test-Path "profile.yaml")) {
    Write-Host "Creating profile.yaml from profile.example.yaml..." -ForegroundColor Yellow
    Copy-Item "profile.example.yaml" "profile.yaml"
    Write-Host "Please edit profile.yaml with your details" -ForegroundColor Yellow
    Write-Host ""
}

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host ""
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
python -m pip install -r requirements.txt
Write-Host ""

# Install new dependencies for enhancements
Write-Host "Installing additional dependencies..." -ForegroundColor Yellow
python -m pip install flask-socketio python-socketio cryptography pytest pytest-flask
Write-Host ""

# Check if frontend node_modules exists
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    npm install socket.io-client
    Set-Location ..
    Write-Host ""
} else {
    Write-Host "Installing new frontend dependency..." -ForegroundColor Yellow
    Set-Location frontend
    npm install socket.io-client
    Set-Location ..
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Servers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start Backend (Flask)
Write-Host "Starting Backend (Flask) on port 5000..." -ForegroundColor Green
Start-Process cmd -ArgumentList "/k cd /d `"$scriptPath`" && .venv\Scripts\activate.bat && python backend\app.py" -WindowStyle Normal

# Wait for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start Frontend (React)
Write-Host "Starting Frontend (React) on port 3000..." -ForegroundColor Green
Start-Process cmd -ArgumentList "/k cd /d `"$scriptPath\frontend`" && npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Servers started successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend URL: http://127.0.0.1:5000" -ForegroundColor White
Write-Host "Frontend URL: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Open your browser to: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: Two new terminal windows have opened:" -ForegroundColor Yellow
Write-Host "  - Backend Server (Flask)" -ForegroundColor White
Write-Host "  - Frontend Server (React)" -ForegroundColor White
Write-Host ""
Write-Host "Close those windows to stop the servers." -ForegroundColor Yellow
Write-Host ""
