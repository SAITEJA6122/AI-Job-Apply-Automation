# Naukri Job Apply - All-in-One Script
# This script handles the complete workflow in one command

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Naukri Job Application Automation" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to project directory
$projectPath = "C:\Users\saite\Downloads\naukri-job-apply-ai-main\naukri-job-apply-ai-main"
Set-Location $projectPath
Write-Host "✓ Changed to project directory" -ForegroundColor Green

# Activate virtual environment
Write-Host "✓ Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Check if session file exists
if (Test-Path "session_naukri.json") {
    $sessionContent = Get-Content "session_naukri.json" -Raw
    if ($sessionContent -match "cookies" -and $sessionContent -match "origins") {
        Write-Host "✓ Login session found and valid" -ForegroundColor Green
        $captureSession = $false
    } else {
        Write-Host "⚠ Login session file exists but appears empty/invalid" -ForegroundColor Yellow
        $captureSession = $true
    }
} else {
    Write-Host "⚠ No login session found" -ForegroundColor Yellow
    $captureSession = $true
}

# Capture login session if needed
if ($captureSession) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  STEP 1: CAPTURE LOGIN SESSION" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "A browser window will open. Please:" -ForegroundColor Yellow
    Write-Host "  1. Log in to Naukri with your credentials" -ForegroundColor White
    Write-Host "  2. Complete any 2FA/OTP if required" -ForegroundColor White
    Write-Host "  3. Once you see your Naukri homepage, return here and press Enter" -ForegroundColor White
    Write-Host ""
    Write-Host "Press Enter to open browser for login..." -ForegroundColor Cyan
    $null = Read-Host
    
    python login_capture.py naukri
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Login session captured successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Login capture failed. Please try again." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Skipping login capture (session already valid)" -ForegroundColor Green
}

# Run job application
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  STEP 2: RUN JOB APPLICATIONS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting job application process..." -ForegroundColor Yellow
Write-Host "Your profile will be used to apply to matching jobs." -ForegroundColor White
Write-Host ""
Write-Host "Target Roles:" -ForegroundColor Cyan
Write-Host "  - Full Stack Developer" -ForegroundColor White
Write-Host "  - MERN Stack Developer" -ForegroundColor White
Write-Host "  - React Developer" -ForegroundColor White
Write-Host "  - Node.js Developer" -ForegroundColor White
Write-Host "  - Frontend Developer" -ForegroundColor White
Write-Host ""
Write-Host "Settings:" -ForegroundColor Cyan
Write-Host "  - Max applications: 5" -ForegroundColor White
Write-Host "  - Experience range: 0-2 years" -ForegroundColor White
Write-Host "  - Salary range: 2.5-3.5 LPA" -ForegroundColor White
Write-Host "  - Locations: Warangal + willing to relocate" -ForegroundColor White
Write-Host ""
Write-Host "⚠  Be ready to answer screening questions in the terminal when prompted!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Enter to start job applications..." -ForegroundColor Cyan
$null = Read-Host

python naukri_apply.py

# Show results
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  APPLICATION COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Results saved to: applications_log.csv" -ForegroundColor Green
Write-Host ""
Write-Host "Press Enter to view the log file..." -ForegroundColor Cyan
$null = Read-Host

if (Test-Path "applications_log.csv") {
    Get-Content applications_log.csv
}

Write-Host ""
Write-Host "✓ Process completed!" -ForegroundColor Green
Write-Host ""