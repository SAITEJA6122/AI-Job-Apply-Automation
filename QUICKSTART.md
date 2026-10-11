# Quick Start Guide

## Prerequisites

- Python 3.10+ installed
- Node.js 16+ installed
- Naukri account with resume uploaded

## Setup (One-Time)

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Playwright browser
playwright install chromium

# 5. Install frontend dependencies
cd frontend
npm install
cd ..

# 6. Configure environment
cp .env.example .env
cp profile.example.yaml profile.yaml

# 7. Edit .env and add your Gemini API key
# Get your free key from: https://aistudio.google.com/apikey
```

## Running the Project

### Option 1: One-Click Start (Recommended)

**Windows:**
```bash
start_project.bat
```

**Linux/Mac:**
```bash
chmod +x start_project.sh
./start_project.sh
```

This will:
- Start Flask backend on http://127.0.0.1:5000
- Start React frontend on http://localhost:3000
- Open both in separate terminal windows

### Option 2: Manual Start

**Terminal 1 (Backend):**
```bash
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
python backend/app.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
# or: yarn dev
```

Then open: **http://localhost:3000**

## First Time Use

1. **Open browser to http://localhost:3000**

2. **Capture Login Session** (for automation):

   **Option 1: Using the batch script (Windows - Easiest)**
   ```bash
   connect_naukri.bat
   ```

   **Option 2: Using command line**
   ```bash
   python login_capture.py naukri
   ```

   **What happens:**
   - Browser will open at Naukri login page
   - Log in to Naukri manually (password, 2FA, CAPTCHA)
   - Once you see your Naukri homepage, return to terminal and press Enter
   - Session saved to `session_naukri.json`
   - Your password is NEVER stored - only session cookies/tokens

3. **Use the Web Dashboard**:
   - Upload your resume (PDF, DOC, DOCX)
   - Configure your profile (roles, skills, experience, location)
   - Click "Save Profile"
   - Click "Start Automation"

## Stopping the Servers

**If using startup script:**
- Press Ctrl+C in the terminal
- Or close the terminal windows

**If running manually:**
- Close both terminal windows
- Or press Ctrl+C in each terminal

## Troubleshooting

**Backend not starting?**
- Check if port 5000 is already in use
- Ensure virtual environment is activated
- Verify Python dependencies are installed

**Frontend not starting?**
- Check if port 3000 is already in use
- Ensure node_modules exists (run `npm install` in frontend/)
- Try `yarn dev` instead of `npm run dev`

**Session expired?**
- Run `python login_capture.py naukri` again to capture a new session

**Need more help?**
- See full README.md for detailed documentation
- Check SETUP_GUIDE.md for complete setup instructions
