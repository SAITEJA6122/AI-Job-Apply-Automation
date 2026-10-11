# Naukri Job Application Automation

A production-ready automation tool with modern web dashboard that searches Naukri.com for jobs matching your profile, applies to them with safety controls, and manages application state.

## ⚡ Quick Start (Run the Project)

**Windows:**
```bash
start_project.bat
```

**Linux/Mac:**
```bash
chmod +x start_project.sh
./start_project.sh
```

Then open your browser to: **http://localhost:3000**

This will start both the Flask backend (port 5000) and React frontend (port 3000) automatically.

---

## 🚀 Features

- **Modern Web Dashboard**: React + TypeScript frontend with real-time updates
- **Secure Session Management**: 24-hour automatic session deletion
- **Resume Parsing**: Automatic extraction of resume data (PDF, DOC, DOCX)
- **Profile Management**: Complete profile configuration UI
- **No Password Storage**: Session-based authentication only
- **Real-Time Monitoring**: Live automation status and progress
- **Live Screen Capture**: Watch the browser applying to jobs in real-time
- **Real-Time Data**: Dashboard statistics update as applications happen

## 📖 Quick Start

For complete setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)

### Quick Setup

```bash
# Python Backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
playwright install chromium

# Frontend
cd frontend
npm install
cd ..

# Configure
cp .env.example .env
cp profile.example.yaml profile.yaml
```

### 🚀 Running the Project

**Option 1: One-Click Start (Recommended for Windows)**

Simply double-click or run:
```bash
start_project.bat
```

This will automatically:
- Start the Flask backend server (http://127.0.0.1:5000)
- Start the React frontend server (http://localhost:3000)
- Open both in separate terminal windows

**Option 2: One-Click Start (Linux/Mac)**

```bash
chmod +x start_project.sh
./start_project.sh
```

**Option 3: Manual Start (Both Platforms)**

Terminal 1 (Backend):
```bash
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
python backend/app.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
# or: yarn dev
```

Then open your browser to: **http://localhost:3000**

## 🎯 Features

## ⚠️ Important Security Notice

**This automates actions against Naukri's terms of service.** Naukri (like
most job platforms) prohibits automated applying, and can detect and
suspend accounts for bot-like activity. This tool includes multiple safety
features to reduce risk (pacing between actions, stopping instantly on CAPTCHA/rate-limit,
using real browser sessions, strict limits) but **cannot eliminate the risk**.
Use at your own discretion.

**This project never stores or uses credentials.** Authentication is session-based:
- You log in manually once via the web dashboard or `login_capture.py`
- Session cookies/tokens are saved to `session_naukri.json` (gitignored)
- No passwords or credentials are ever stored in code or config files

**Run from residential IP only.** Naukri blocks traffic from cloud hosting (AWS, GCP, etc.).
Run from your home computer or personal network.

## Features

### Core Functionality
- **Automated Job Search**: Searches Naukri for your configured target roles
- **Smart Filtering**: Filters by experience, location, company, seniority, and role keywords
- **Role Family Matching**: Cross-role matching for broader job discovery
- **Global Freshness Phases**: Prioritizes 7-day jobs, then 30-day jobs when exhausted
- **Automated Applications**: Applies to matching jobs with human-in-the-loop for sensitive questions
- **Screening Question Handling**: AI-assisted answers (OpenRouter/Groq/Gemini) for open-text questions
- **Application Verification**: Confirms each application before logging as successful
- **Live Screen Capture**: Watch the browser applying to jobs in real-time

### Security & Safety Hardening
- **Security Controller**: Centralized security detection and fail-closed behavior
- **Pre-Action Safety Checks**: Security verification before every browser action
- **CAPTCHA Detection**: Stops entire run on CAPTCHA challenges
- **Rate Limit Detection**: Stops on rate-limit warnings
- **Authentication Failure Detection**: Stops on auth errors
- **Emergency Stop**: Configurable emergency stop functionality
- **Session Security**: Session-based auth (no credentials stored)
- **Secret Scanner**: Detects and prevents credential exposure
- **Privacy Controls**: LLM data sharing configurable (disabled by default)

### State Management & Reliability
- **Application State Machine**: Persistent state tracking per job
- **Duplicate Protection**: Prevents duplicate applications
- **Crash Recovery**: Resumes safely after crashes
- **Application Limits**: Enforces hourly and daily limits
- **Per-Run Limits**: Configurable max applications per run
- **Comprehensive Logging**: CSV logs, JSON stats, security event logs
- **Real-Time Stats Autosave**: Statistics update every 20 jobs seen, every 10 skips, immediately after each application

### Enhanced Features
- **Email Notifications**: Receive email summaries after application runs
- **Scheduling**: Schedule automatic runs at specific times
- **Export to Excel/CSV**: Export application logs and statistics
- **Modern Web Dashboard**: Beautiful, responsive UI with real-time updates
- **Resume Auto-Extraction**: Auto-detects skills, experience, education from resume
- **Live Screen Viewing**: Floating window to watch browser automation in real-time

### Filtering & Matching
- **Target Roles**: Configurable target roles (Full Stack, MERN, React, Node.js, Frontend, Backend, etc.)
- **Experience Filtering**: Fresher profile with seniority exclusion
- **Location Preferences**: Preferred locations with relocation support
- **Company Filtering**: Include/exclude specific companies
- **Title Keywords**: Permissive role keyword matching
- **Role Family Groups**: Cross-role matching within technology families

## Requirements

- Python 3.10+
- A Naukri account with resume uploaded
- API key for screening questions (OpenRouter/Groq/Gemini)
- Residential IP (not cloud hosting)

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd naukri-job-apply-ai-main
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure API Keys

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
OPENROUTER_API_KEY=your-openrouter-api-key
GROQ_API_KEY=your-groq-key  # optional fallback
GEMINI_API_KEY=your-gemini-key  # optional fallback
```

Get API keys from:
- OpenRouter: https://openrouter.ai/keys
- Groq: https://console.groq.com/keys
- Gemini: https://aistudio.google.com/apikey

### 3. Configure Profile

```bash
cp profile.example.yaml profile.yaml
```

Edit `profile.yaml` with:
- Target roles
- Experience range
- Preferred locations
- Salary expectations
- Skills and work history

### 4. Capture Login Session

**Option 1: Using Web Dashboard (Recommended)**
1. Open http://localhost:3000 in your browser
2. Click "Connect Naukri" button
3. A browser window opens at the Naukri login page
4. Log in manually (password, 2FA, CAPTCHA - all by you)
5. Once you see your Naukri homepage, the session is saved
6. Session lasts 12 hours, then automatically expires

**Option 2: Using Command Line**
```bash
python login_capture.py naukri
```

A browser opens. Log in manually, then press Enter in terminal.
Session saved to `session_naukri.json` (gitignored - treat as sensitive).

### 5. Run the Project

**Start both servers at once:**

Windows:
```bash
start_project.bat
```

Linux/Mac:
```bash
chmod +x start_project.sh
./start_project.sh
```

**Or start manually:**

Terminal 1 (Backend):
```bash
.venv\Scripts\activate
python backend/app.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

Then open your browser to: **http://localhost:3000**

### 6. Using the Web Dashboard

The web dashboard allows you to:
- Upload your resume (PDF, DOC, DOCX) - auto-extracts skills, experience, education
- Configure your profile (role, skills, experience, location, salary)
- Connect your Naukri account
- Start/stop automation with one click
- View application statistics in real-time
- Watch live screen capture of browser automation
- Export logs and statistics to Excel/CSV

**Steps:**
1. Open http://localhost:3000 in your browser
2. Upload your resume (optional - will auto-fill profile data)
3. Configure your profile:
   - Select target roles (multiple selection supported)
   - Set experience range and salary expectations
   - Add preferred locations
   - Add skills (auto-filled from resume)
4. Connect your Naukri account
5. Click "Start Automation" to begin applying to jobs
6. Click "Live Screen" to watch the browser in real-time
7. Monitor real-time statistics and export results

### 7. Alternative: Command Line Automation

If you prefer command line over the web dashboard:

```bash
python naukri_apply.py
```

Or use the batch script (Windows):
```bash
.\run.bat
```

## Configuration

### Application Limits (profile.yaml)

```yaml
# Per-run limit
stop_after_n_applications: 20

# Rate limits
max_applications_per_hour: 20
max_applications_per_day: 40

# Freshness phases
job_freshness_days_phase1: 7   # Search last 7 days first
job_freshness_days_phase2: 30  # Then last 30 days
```

### Safety Settings (profile.yaml)

```yaml
# Stop conditions
stop_on_captcha: true
stop_on_rate_limit: true
stop_on_authentication_error: true
emergency_stop_enabled: true

# Privacy
llm_data_sharing: false
save_debug_artifacts: false
```

### Screen Capture Settings (profile.yaml)

```yaml
# Live screen capture
enable_screen_capture: true
screen_capture_interval: 2  # seconds between screenshots
```

### Target Roles

Configure target roles including:
- Full Stack Developer
- MERN Stack Developer
- React Developer
- Node.js Developer
- Frontend Developer
- Backend Developer
- Software Developer
- Software Engineer
- Junior Software Engineer
- And more...

## Security Best Practices

1. **Never commit credentials** - Session files are gitignored
2. **Keep .env private** - Contains API keys
3. **Keep profile.yaml private** - Contains personal info
4. **Review logs before sharing** - May contain job data
5. **Run from personal network** - Avoid cloud IPs
6. **Monitor for security events** - Check `security_events.jsonl`

## Project Structure

```
backend/
  app.py                     Flask backend server
  resumes/                   Uploaded resumes storage
  sessions.db                Session database
frontend/
  src/                       React + TypeScript source
  index.html                 Entry HTML
  package.json               Frontend dependencies
naukri_apply.py              Main automation script
login_capture.py             Session capture
scheduler.py                 Job scheduling (auto-run at times)
profile.yaml                 Your profile (gitignored)
session_naukri.json          Login session (gitignored)
common/
  application_state.py       State machine
  application_limiter.py     Rate limiting
  security_controller.py     Security detection
  profile.py                 Profile loader
  llm.py                     LLM integration (OpenRouter/Groq/Gemini)
  openrouter_llm.py           OpenRouter LLM integration
  groq_llm.py                Groq LLM integration
  gemini.py                  Gemini LLM integration
  retry_handler.py           Bounded retries
  safety_config.py           Safety settings
  notifications.py           Email notifications
  export_utils.py            Export to Excel/CSV
  human_behavior.py          Human-like browser behavior
start_project.bat            Windows startup script (runs both servers)
start_project.sh             Linux/Mac startup script (runs both servers)
```

## Web Dashboard Features

The web dashboard provides a user-friendly interface with React + TypeScript frontend:

### Features
- **Resume Upload**: Upload your resume directly from the browser (PDF, DOC, DOCX)
- **Profile Configuration**: Set your role, skills, experience, and preferences
- **Naukri Connection**: Connect your Naukri account with one click
- **One-Click Automation**: Start/stop automation with a single button
- **Real-Time Statistics**: View application statistics (applied, skipped, errors, success rate)
- **Live Screen Capture**: Watch the browser applying to jobs in real-time
- **Responsive Design**: Works on desktop and mobile devices
- **Resume Parsing**: Automatic extraction of skills, experience, education from resume
- **Export Data**: Export logs and statistics to Excel/CSV
- **Settings Page**: Configure automation settings, screen capture, and API keys

### Using the Web Dashboard

**Step 1: Start the servers**
```bash
# Windows
start_project.bat

# Linux/Mac
./start_project.sh
```

**Step 2: Open in browser**
- Open your browser to: **http://localhost:3000**

**Step 3: Use the dashboard**
1. Upload your resume (PDF, DOC, DOCX) - auto-extracts skills, experience, education
2. Configure your profile:
   - Select target roles (multiple selection supported)
   - Set experience, CTC, location
   - Add skills (auto-filled from resume)
3. Connect your Naukri account
4. Configure API keys in Settings
5. Configure screen capture settings
6. Click "Start Automation"
7. Click "Live Screen" to watch the browser in real-time
8. Monitor real-time statistics and export results

### Stopping the Servers

**If using start_project.bat/sh:**
- Press Ctrl+C in the terminal to stop both servers
- Or close the terminal windows

**If running manually:**
- Close both terminal windows (backend and frontend)
- Or press Ctrl+C in each terminal

## Advanced Features

### Email Notifications

Configure email notifications to receive summaries after each automation run:

1. Edit `.env` file:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_FROM_EMAIL=your-email@example.com
NOTIFICATION_TO_EMAIL=your-email@example.com
```

2. The system will automatically send email summaries with:
   - Total applications submitted
   - Success rate
   - Jobs by role
   - Skip reasons
   - Error categories

**Note**: For Gmail, use an App Password (not your regular password). Enable 2FA and generate an App Password from Google Account settings.

### Scheduling

Schedule automatic runs at specific times:

**Option 1: Command Line Scheduler**

```bash
# Run at specific times daily (e.g., 9 AM, 2 PM, 6 PM)
python scheduler.py times --times "09:00,14:00,18:00"

# Run after a delay (e.g., 30 minutes from now)
python scheduler.py delay --minutes 30

# Run at fixed intervals (e.g., every 2 hours)
python scheduler.py interval --minutes 120

# Run at intervals with max runs (e.g., every 3 hours, max 5 runs)
python scheduler.py interval --minutes 180 --max-runs 5
```

**Option 2: Windows Task Scheduler**

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily at specific time)
4. Action: Start a program
5. Program: `python`
6. Arguments: `scheduler.py times --times "09:00,14:00,18:00"`
7. Start in: `<your-project-directory>`

**Option 3: Use Batch Script**

```bash
# Edit schedule_tasks.bat with your preferred times
# Then add to Windows Task Scheduler
.\schedule_tasks.bat
```

### Export to Excel/CSV

Export application data for analysis:

**Via Web Dashboard:**
1. Open web dashboard
2. Go to Applications page
3. Click export buttons:
   - Export Log (CSV)
   - Export Log (Excel)
   - Export Stats (CSV)
   - Export Stats (Excel)

**Via Command Line:**
```bash
# Export application log
python -c "from common.export_utils import export_application_log; export_application_log(output_format='excel')"

# Export statistics
python -c "from common.export_utils import export_statistics; export_statistics(output_format='excel')"
```

Exports include:
- Application log: Full history of all job applications
- Statistics: Summary by role, success rates, skip reasons
- Formatted Excel with styling and auto-sized columns
- CSV with UTF-8 encoding for Excel compatibility

## Deployment to Git

This project is configured for safe Git deployment:

### Files Excluded (.gitignore)
- Session files (`session_*.json`)
- API keys (`.env`)
- Personal profile (`profile.yaml`)
- Application state
- Security logs
- Debug artifacts
- Virtual environments
- Screenshots directory

### To Deploy

```bash
# Initialize Git (if not already)
git init

# Add files (excludes gitignored files automatically)
git add .

# Commit
git commit -m "Initial commit: Naukri job automation with security hardening"

# Add remote
git remote add origin <your-repo-url>

# Push
git push -u origin main
```

### After Cloning

When someone clones your repo, they need to:

1. Copy `profile.example.yaml` → `profile.yaml` and configure
2. Copy `.env.example` → `.env` and add API keys
3. Run the web dashboard and connect Naukri account via the UI
4. Start automation

## Troubleshooting

**Session expired?**
- Reconnect via the web dashboard or run `python login_capture.py naukri`

**Hourly limit reached?**
- Wait 1 hour OR
- Increase `max_applications_per_hour` in profile.yaml

**CSS selectors broken?**
- Naukri changes markup periodically
- Inspect page HTML and update selectors in `naukri_apply.py`

**LLM not answering screening questions?**
- Check your API key is configured in `.env`
- Check the LLM fallback chain: OpenRouter → Groq → Gemini
- Check backend logs for LLM errors

**Live screen not working?**
- Ensure `enable_screen_capture: true` in profile.yaml
- Ensure browser mode is set to "visible"
- Check screenshots directory exists

## License

MIT - Use, modify, and share freely. No warranty provided.

## Disclaimer

This tool is for educational purposes. Users are responsible for:
- Compliance with Naukri's terms of service
- Account security and consequences
- Reviewing and understanding all code before use
