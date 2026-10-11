@echo off
cd /d "C:\Users\saite\Downloads\naukri-job-apply-ai-main\naukri-job-apply-ai-main"
call .\.venv\Scripts\activate.bat
powershell -ExecutionPolicy Bypass -File run_all.ps1
pause