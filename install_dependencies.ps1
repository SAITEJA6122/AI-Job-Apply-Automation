# PowerShell Install Dependencies Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installing Dependencies" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment." -ForegroundColor Red
        Write-Host "Please ensure Python is installed and accessible." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "Virtual environment created successfully." -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# Upgrade pip first
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host ""

# Install backend dependencies
Write-Host "Installing backend dependencies from requirements.txt..." -ForegroundColor Yellow
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install backend dependencies." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Install new dependencies for enhancements
Write-Host "Installing additional dependencies (WebSocket, SSL, Testing)..." -ForegroundColor Yellow
python -m pip install flask-socketio python-socketio cryptography pytest pytest-flask
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Some additional dependencies failed to install." -ForegroundColor Yellow
    Write-Host "The project may still work, but some features will be unavailable." -ForegroundColor Yellow
    Write-Host ""
}
Write-Host ""

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install frontend dependencies." -ForegroundColor Red
    Set-Location ..
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Install socket.io-client for frontend
Write-Host "Installing socket.io-client for WebSocket support..." -ForegroundColor Yellow
npm install socket.io-client
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: socket.io-client installation failed." -ForegroundColor Yellow
    Write-Host "Real-time progress features may not work." -ForegroundColor Yellow
    Write-Host ""
}
Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "All dependencies have been installed successfully." -ForegroundColor White
Write-Host "You can now run the project using:" -ForegroundColor Cyan
Write-Host "  - .\run_both_servers.ps1" -ForegroundColor White
Write-Host "  - Or .\setup_and_run.ps1" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
