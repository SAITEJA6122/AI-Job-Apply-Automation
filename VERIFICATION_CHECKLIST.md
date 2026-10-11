# Naukri Job Apply AI - Verification Checklist

This checklist ensures the project is properly configured to apply to real jobs on Naukri.

## ✅ Prerequisites Checklist

### 1. Environment Setup
- [x] Python installed (3.8+)
- [x] Node.js installed (16+)
- [x] Project dependencies installed (run `.\install_dependencies.ps1`)
- [x] python-dotenv installed (added to requirements.txt)

### 2. Configuration Files
- [x] `.env` file exists in project root
- [ ] **CRITICAL:** `GEMINI_API_KEY` configured in `.env` file
  - Get free key from: https://aistudio.google.com/apikey
  - Replace `your-gemini-api-key-here` with actual key
- [ ] Optional: `GROQ_API_KEY` configured (fallback if Gemini quota exhausted)
  - Get key from: https://console.groq.com/keys

### 3. Profile Configuration
- [x] `profile.yaml` exists
- [x] Contains your personal details (name, email, phone)
- [x] Contains skills extracted from resume
- [x] Contains target roles (job titles to search for)
- [x] Contains preferred locations
- [x] Contains salary expectations
- [ ] **Verify:** Current CTC and Expected CTC are set correctly
- [ ] **Verify:** Notice period is set correctly
- [ ] **Verify:** Years of experience is accurate

### 4. Resume File
- [ ] Resume file exists in project root (e.g., `resume.pdf`)
- [ ] Resume file name matches `resume_file_name` in `profile.yaml`
- [ ] Resume has been uploaded and approved via the web UI

### 5. Naukri Session
- [ ] Naukri credentials ready (email and password)
- [ ] Session will be created via web UI login
- [ ] `session_naukri.json` will be created after successful login

## 🔧 Backend Verification

### 1. Backend Server
- [x] Flask backend configured
- [x] CORS enabled
- [x] Rate limiting configured (1000/day, 200/hour)
- [x] WebSocket configured for real-time updates
- [x] Automation subprocess configured
- [x] API key validation added to automation start

### 2. API Endpoints
- [x] `/api/naukri/login` - Login to Naukri
- [x] `/api/automation/start` - Start automation (validates session, profile, API keys)
- [x] `/api/automation/stop` - Stop automation
- [x] `/api/automation/status` - Check automation status
- [x] `/api/stats` - Get application statistics
- [x] `/api/applications` - Get application history
- [x] `/api/api-keys` - Save/get API keys
- [x] `/api/resume/upload` - Upload resume
- [x] `/api/resume/approve` - Approve resume data
- [x] `/api/profile` - Get/update profile

### 3. Security Features
- [x] Session auto-deletion after 12 hours
- [x] Passwords never stored
- [x] Input validation and sanitization
- [x] Rate limiting on all endpoints
- [x] CAPTCHA detection and stop
- [x] Rate limit detection and stop

## 🎨 Frontend Verification

### 1. Pages
- [x] Dashboard - Shows automation status, stats, charts
- [x] Profile - View and edit profile
- [x] Resume - Upload and approve resume
- [x] Job Preferences - Configure target roles, locations, salary
- [x] Applications - View application history with export
- [x] Settings - Configure automation, API keys, notifications

### 2. Features
- [x] Dark mode support
- [x] Real-time updates via WebSocket
- [x] Statistics charts (bar and pie charts)
- [x] Export to CSV and JSON
- [x] Mobile responsive design
- [x] Toast notifications
- [x] Confirmation dialogs
- [x] Terminal output display

### 3. Automation Flow
- [x] Upload resume → Parse → Approve → Update profile
- [x] Configure job preferences (roles, locations, salary)
- [x] Login to Naukri → Create session
- [x] Configure API keys (Gemini for AI responses)
- [x] Start automation → Apply to jobs
- [x] Monitor progress → View results

## 🚀 Step-by-Step to Apply to Real Jobs

### Step 1: Install Dependencies
```powershell
cd "C:\Users\saite\Desktop\naukri-job-apply-ai-main - Copy\naukri-job-apply-ai-main"
.\install_dependencies.ps1
```

### Step 2: Configure API Key
1. Open `.env` file in project root
2. Replace `your-gemini-api-key-here` with your actual Gemini API key
3. Get free key from: https://aistudio.google.com/apikey
4. Save the file

**OR use the Settings page:**
1. Go to Settings page in the web UI
2. Enter your Gemini API key
3. Click "Save API Keys"

### Step 3: Start Servers
```powershell
.\run_both_servers.ps1
```

This will start:
- Backend: http://127.0.0.1:5000
- Frontend: http://localhost:3000

### Step 4: Upload and Approve Resume
1. Go to http://localhost:3000/resume
2. Upload your resume (PDF/DOC/DOCX)
3. Review extracted data (skills, experience, education, target roles)
4. Edit if needed
5. Click "Approve & Save to Profile"

### Step 5: Configure Job Preferences
1. Go to http://localhost:3000/preferences
2. Set target roles (e.g., "Full Stack Developer", "React Developer")
3. Add preferred locations (e.g., "Bangalore", "Hyderabad")
4. Set salary expectations (current and expected CTC)
5. Add companies to blacklist if needed
6. Click "Save Preferences"

### Step 6: Login to Naukri
1. Go to http://localhost:3000/dashboard
2. Click "Connect Naukri Account"
3. Enter your Naukri email and password
4. Click "Connect & Start"
5. Wait for login to complete (browser automation will login)
6. Session will be created and stored

### Step 7: Start Automation
1. On Dashboard, verify:
   - Naukri Account Status: Connected
   - Resume Status: Resume uploaded and profile populated
   - API Key: Configured (check Settings page)
2. Click "Start Automation"
3. Monitor progress in:
   - Live Progress section
   - Terminal Output section
   - Statistics cards
4. Automation will:
   - Search for matching jobs based on your profile
   - Apply to relevant jobs
   - Answer screening questions using AI
   - Log all applications

### Step 8: Monitor Results
1. Watch the Dashboard for real-time updates
2. Go to Applications page to see detailed history
3. Export applications to CSV/JSON for analysis
4. Check statistics charts for insights

## ⚠️ Important Notes

### Before Starting Automation
1. **API Key Required:** You MUST configure the GEMINI_API_KEY in `.env` or Settings page
2. **Profile Complete:** Ensure your profile.yaml has all required fields
3. **Resume Approved:** Resume must be uploaded and approved
4. **Session Active:** Must be logged in to Naukri
5. **Preferences Set:** Target roles and locations configured

### During Automation
1. **Monitor Progress:** Watch the terminal output for errors
2. **CAPTCHA:** If CAPTCHA appears, automation will stop - solve it manually
2. **Rate Limits:** If rate limited, automation will stop - wait and retry
3. **Session Expiry:** Session expires after 12 hours - re-login if needed

### After Automation
1. **Review Applications:** Check Applications page for all applications
2. **Export Data:** Export to CSV/JSON for record-keeping
3. **Update Profile:** Update preferences if needed
4. **Disconnect:** Can disconnect Naukri session from Dashboard

## 🔍 Troubleshooting

### Issue: "GEMINI_API_KEY not configured"
**Solution:** Configure API key in `.env` file or Settings page

### Issue: "No active Naukri session"
**Solution:** Login to Naukri from Dashboard first

### Issue: "No profile configured"
**Solution:** Upload and approve resume from Resume page

### Issue: Automation stops immediately
**Solution:** Check terminal output for error message, fix configuration

### Issue: WebSocket connection error
**Solution:** Refresh browser, backend should auto-reload

### Issue: Applications not showing
**Solution:** Click Refresh button on Applications page

## 📊 Current Project Status

### ✅ Completed Features
- Full web UI with all pages
- Real-time progress monitoring
- Statistics charts and analytics
- Export functionality (CSV/JSON)
- Mobile responsive design
- Dark mode support
- API key management
- Job preferences configuration
- Resume upload and parsing
- Profile management
- Automation control (start/stop)
- Application history
- Security features (CAPTCHA, rate limit detection)

### ⚠️ Configuration Required
- **CRITICAL:** GEMINI_API_KEY must be configured
- Profile must be complete and accurate
- Resume must be uploaded and approved
- Naukri session must be active

### 🎯 Ready to Apply to Real Jobs
Once you complete the "Configuration Required" items above, the project is ready to apply to real jobs on Naukri!

## 📝 Additional Tips

1. **Start Small:** Set `stop_after_n_applications` to 5-10 for testing
2. **Monitor Closely:** Watch the first few applications carefully
3. **Adjust Preferences:** Update target roles and locations based on results
4. **Check Logs:** Review `applications_log.csv` for detailed history
5. **Backup Data:** Export applications regularly

## 🎉 Success Indicators

You'll know it's working when:
- Dashboard shows "Naukri Account Status: Connected"
- Dashboard shows "Resume Status: Resume uploaded and profile populated"
- Settings shows "✓ Configured" for Gemini API key
- Automation starts without errors
- Terminal shows "Starting automation process..."
- Terminal shows jobs being found and applied
- Applications page shows entries after automation starts
- Statistics cards update in real-time

---

**Last Updated:** October 9, 2026
**Project Status:** Ready for real job applications (pending API key configuration)
