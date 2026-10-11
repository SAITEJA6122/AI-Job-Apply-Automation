@echo off
REM Example Windows Task Scheduler batch script
REM This script runs the job automation at 9 AM, 2 PM, and 6 PM daily

cd /d "%~dp0naukri-job-apply-ai-main"

python scheduler.py times --times "09:00,14:00,18:00"
