# Production Readiness Guide

## Changes Made for Production-Ready Deployment

### 1. Real Job Applications (No Fake/Dry-Run Mode)
- ✅ **Fixed**: Backend now validates `dry_run` mode before starting automation
- ✅ **Action**: If `dry_run: true` is detected, automation will not start and user is warned
- ✅ **Current Status**: `dry_run: false` in profile.yaml - ready for real applications

### 2. Python Environment Configuration
- ✅ **Fixed**: Backend now uses virtual environment Python (`.venv/Scripts/python.exe`)
- ✅ **Validation**: Checks if venv Python exists before starting automation
- ✅ **Result**: No more "ModuleNotFoundError: No module named 'playwright'"

### 3. Real-Time Data Updates
- ✅ **Fixed**: Stats are auto-saved during automation (every 20 jobs seen, every 10 skips, immediately after each application)
- ✅ **Fixed**: Dashboard refreshes every 2 seconds when automation is running
- ✅ **Fixed**: Applications page refreshes every 3 seconds
- ✅ **Result**: Users see real-time progress, not cached old data

### 4. Duplicate Protection Reset
- ✅ **Fixed**: Application state is automatically reset before each new run
- ✅ **Fixed**: Old job records (5,729 from October 1 & 7) are cleared
- ✅ **Result**: Each run starts fresh, jobs aren't skipped as duplicates from previous runs

### 5. CSV Logging
- ✅ **Fixed**: Added `f.flush()` to force immediate write to disk
- ✅ **Result**: Applications are logged immediately, not buffered

### 6. WebSocket Real-Time Streaming
- ✅ **Added**: Subprocess output is streamed to frontend via WebSocket
- ✅ **Added**: Console logging for debugging
- ✅ **Added**: Automatic status broadcast when process ends
- ✅ **Result**: TerminalOutput shows real logs, not fake sample data

### 7. Error Handling & User Feedback
- ✅ **Added**: Detailed error messages in Dashboard toast notifications
- ✅ **Added**: Validation for all prerequisites before starting
- ✅ **Added**: WebSocket connection logging in browser console
- ✅ **Result**: Users get clear feedback on what's wrong

### 8. Configuration Validation
- ✅ **Added**: Check for active Naukri session
- ✅ **Added**: Check for profile configuration
- ✅ **Added**: Check for API key (Gemini/Groq/OpenRouter)
- ✅ **Added**: Check for virtual environment Python
- ✅ **Added**: Check for dry_run mode
- ✅ **Result**: Clear error messages if any prerequisite is missing

## Current Configuration Status

### ✅ Verified:
- **API Key**: OpenRouter API key configured and valid
- **Dry-Run Mode**: Disabled (`dry_run: false`)
- **Profile**: Complete with skills, experience, and preferences
- **Python Environment**: Virtual environment properly set up
- **Session**: Naukri session active and valid

### 📊 Data Files Reset:
- **application_stats.json**: Reset to 0 (ready for new run)
- **application_state.json**: Cleared of old records (ready for new run)
- **applications_log.csv**: Will receive new entries during run

## How to Use (For Clients)

### 1. Initial Setup (One-Time)
1. **Upload Resume**: Go to Resume page → Upload PDF → Approve extracted data
2. **Configure Profile**: Verify skills, experience, and job preferences
3. **Add API Key**: Go to Settings → Add Gemini/Groq/OpenRouter API key
4. **Login to Naukri**: Go to Dashboard → Login with Naukri credentials

### 2. Starting Automation
1. Go to Dashboard
2. Click "Start Automation"
3. Watch real-time progress in:
   - Live Progress section
   - Terminal Output (click "Show Terminal")
   - Statistics cards (Jobs Found, Applications, Skipped, Success Rate)
4. Applications page shows real-time application history

### 3. Monitoring
- **Stats**: Update every 2 seconds during automation
- **Applications**: Update every 3 seconds
- **Terminal**: Shows real logs from automation process
- **Stop**: Click "Stop Automation" anytime to pause

### 4. After Automation
- **View History**: Go to Applications page to see all applications
- **Export**: Download CSV or JSON of application history
- **Restart**: Can start new run (old state is automatically reset)

## Important Notes for Clients

### ⚠️ Rate Limiting
- Naukri has rate limits to prevent spam
- Current profile: Max 40 applications/day, 20/hour
- Automation will stop if rate limit is hit
- Wait before restarting if rate-limited

### ⚠️ Session Expiration
- Naukri sessions expire after 12 hours
- Will need to re-login after expiration
- You'll see "Session expired" message

### ⚠️ CAPTCHA
- Automation stops on CAPTCHA
- Manual intervention required
- Resume after solving CAPTCHA

### ⚠️ Duplicate Protection
- Within a single run: Won't apply to same job twice
- Between runs: Old state is reset, can re-apply to jobs
- Application logs track all attempts

## Troubleshooting

### Automation Won't Start
- Check: Naukri session is active (Dashboard → Session Status)
- Check: Profile is configured (Dashboard → Resume Status)
- Check: API key is set (Settings → API Key Management)
- Check: Dry-run mode is disabled (Settings → Automation Configuration)

### No Applications Being Made
- Check: Terminal Output for errors
- Check: Job preferences match available jobs
- Check: Location preferences (currently set to Hyderabad only)
- Check: Experience range (currently 0-1 years)

### Old Data Showing
- Stats and application state are automatically reset on each new run
- If still seeing old data, stop automation and restart backend

### WebSocket Not Connecting
- Backend must be running on port 5000
- Check browser console for connection errors
- Refresh the page to reconnect

## Technical Architecture

### Backend (Flask)
- Port: 5000
- WebSocket: Socket.IO for real-time updates
- Subprocess: Runs `naukri_apply.py` in virtual environment
- Auto-reset: Clears state before each run

### Frontend (React)
- Port: 3000
- WebSocket: Socket.IO client for real-time updates
- Refresh intervals: 2s (running), 5s (stopped)
- Terminal: Shows real subprocess output

### Data Files
- `profile.yaml`: User profile and preferences
- `application_stats.json`: Real-time statistics
- `application_state.json`: Job application state (for duplicate protection)
- `applications_log.csv`: Application history log
- `session_naukri.json`: Naukri session cookies

## Support

For issues or questions:
1. Check Terminal Output for error messages
2. Check browser console for WebSocket errors
3. Check backend terminal for subprocess errors
4. Review this document for common issues
