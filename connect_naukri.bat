@echo off
echo ========================================
echo   Naukri Login Session Capture
echo ========================================
echo.
echo This will open a browser window where you can log in to Naukri.
echo.
echo Steps:
echo   1. A browser will open at the Naukri login page
echo   2. Log in with your credentials manually
echo   3. Complete any 2FA or CAPTCHA if required
echo   4. Once you see your Naukri homepage, return here and press Enter
echo   5. Your session will be saved
echo.
echo Press any key to open the browser...
pause >nul

call .venv\Scripts\activate.bat
python login_capture.py naukri

echo.
echo ========================================
echo   Session Capture Complete
echo ========================================
echo.
echo Your Naukri session has been saved to session_naukri.json
echo You can now go to the dashboard and click "Connect Naukri"
echo.
pause
