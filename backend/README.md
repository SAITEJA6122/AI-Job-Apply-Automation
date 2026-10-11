# Backend API Documentation

Enhanced Flask backend for Naukri Job Automation with session management and 24-hour data deletion.

## Features

- **Session Management**: SQLite-based session tracking with automatic 24-hour expiration
- **Security**: No password storage, session-based authentication only
- **Profile Management**: YAML synchronization with profile.yaml
- **Resume Parsing**: Automatic extraction of resume data (PDF, DOC, DOCX)
- **Automation Control**: Start/stop job application automation
- **Automatic Cleanup**: Background worker deletes expired sessions every hour

## Installation

1. **Install Python Dependencies**
```bash
cd naukri-job-apply-ai-main
pip install -r requirements.txt
```

2. **Install Playwright Browsers**
```bash
playwright install chromium
```

3. **Configure Environment Variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

## Database Schema

### naukri_sessions
- `id`: Primary key
- `session_id`: Unique session identifier
- `created_at`: Session creation timestamp
- `expires_at`: Session expiration timestamp (12 hours after creation)
- `status`: Session status (connected/disconnected)
- `browser_profile_path`: Path to temporary browser profile
- `session_file_path`: Path to session file

### users
- `id`: Primary key
- `email`: User email
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

### resumes
- `id`: Primary key
- `user_id`: Foreign key to users
- `filename`: Stored filename
- `original_filename`: Original upload filename
- `file_path`: Path to stored file
- `parsed_data`: JSON string of parsed resume data
- `uploaded_at`: Upload timestamp
- `expires_at`: File expiration timestamp (12 hours after upload)

## API Endpoints

### Health Check
- `GET /api/health` - Health check endpoint

### Session Management
- `GET /api/session/status` - Get current Naukri session status
- `POST /api/naukri/connect` - Initiate Naukri connection flow
- `POST /api/naukri/disconnect` - Disconnect Naukri and delete session data
- `POST /api/session/cleanup` - Manually trigger cleanup of expired sessions

### Profile Management
- `GET /api/profile` - Get current profile configuration
- `POST /api/profile` - Update profile configuration

### Resume Management
- `POST /api/resume/upload` - Upload and parse resume file
- `POST /api/resume/approve` - Approve parsed resume data and sync with profile

### Statistics & Applications
- `GET /api/stats` - Get application statistics
- `GET /api/applications` - Get application history from CSV log

### Automation Control
- `POST /api/automation/start` - Start the automation
- `POST /api/automation/stop` - Stop the automation
- `GET /api/automation/status` - Get automation status

## Security Features

1. **No Password Storage**: Naukri passwords are never stored. Authentication is session-based only.
2. **12-Hour Expiration**: All session data automatically expires after 12 hours.
3. **Automatic Cleanup**: Background worker deletes expired sessions every hour.
4. **Atomic Profile Updates**: Profile YAML updates use atomic writes to prevent corruption.
5. **Secure File Storage**: Resume files stored in protected directory with expiration.

## Running the Backend

### Development Mode
```bash
cd backend
python app.py
```

The backend will run on `http://localhost:5000`

### Production Mode
```bash
# Use gunicorn or similar WSGI server
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

## Session Cleanup

The cleanup system runs automatically:
- **Background Worker**: Runs every hour to delete expired sessions
- **Startup Cleanup**: Runs when the application starts
- **Manual Cleanup**: Can be triggered via API endpoint

Cleanup includes:
- Deletion of session files
- Deletion of browser profiles
- Deletion of temporary resume files
- Removal of expired database records

## Integration with Existing Automation

The backend integrates seamlessly with the existing Python automation:
- Uses existing `profile.yaml` for configuration
- Uses existing `session_naukri.json` for authentication
- Uses existing `naukri_apply.py` for automation
- Uses existing `applications_log.csv` for history
- Uses existing `application_stats.json` for statistics

## Error Handling

All API endpoints return consistent error responses:
```json
{
  "success": false,
  "error": "Error message"
}
```

## Logs

Backend logs are printed to console. For production, configure proper logging to files.

## Troubleshooting

### Database Locked Error
If you encounter database locked errors, ensure only one backend instance is running.

### Session Not Expiring
Check that the cleanup worker is running. Manually trigger cleanup via API endpoint.

### Resume Parsing Failed
Ensure the file is a valid PDF, DOC, or DOCX file. Check file size limits.

## Environment Variables

Required environment variables in `.env`:
- `GEMINI_API_KEY`: Google Gemini API key for AI-powered responses
- `GROQ_API_KEY`: Groq API key (optional fallback)

Optional email notification variables:
- `SMTP_SERVER`: SMTP server for email notifications
- `SMTP_PORT`: SMTP port
- `SMTP_USERNAME`: SMTP username
- `SMTP_PASSWORD`: SMTP password
- `NOTIFICATION_FROM_EMAIL`: From email address
- `NOTIFICATION_TO_EMAIL`: To email address
