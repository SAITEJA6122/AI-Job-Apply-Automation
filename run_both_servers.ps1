# PowerShell Run Both Servers Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Naukri Job Automation" -ForegroundColor Cyan
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
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run .\install_dependencies.ps1 first." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# Start Backend (Flask)
Write-Host "Starting Backend (Flask) on port 5000..." -ForegroundColor Green
Start-Process cmd -ArgumentList "/k cd /d `"$scriptPath`" && .venv\Scripts\activate.bat && python backend\app.py" -WindowStyle Normal

# Wait for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start Frontend (React)
Write-Host "Starting Frontend (React) on port 3000..." -ForegroundColor Green
Start-Process cmd -ArgumentList "/k cd /d `"$scriptPath\frontend`" && yarn run dev" -WindowStyle Normal

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
Write-Host "Two terminal windows have opened:" -ForegroundColor Yellow
Write-Host "  1. Backend Server (Flask) - Keep this open" -ForegroundColor White
Write-Host "  2. Frontend Server (React) - Keep this open" -ForegroundColor White
Write-Host ""
Write-Host "Close those windows to stop the servers." -ForegroundColor Yellow
Write-Host ""
