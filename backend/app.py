"""
Enhanced Backend API for Naukri Job Automation
Provides REST API endpoints for the web frontend with:
- Session management with 24-hour expiration
- Profile management with YAML synchronization
- Resume upload and parsing
- Automation control
- Real-time status updates
"""
import os
import json
import yaml
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import threading
import time

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, continue without it

# Import existing project modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from common.profile import Profile
    from common import llm
    from common.security_controller import get_security_controller
    from common.application_state import get_application_state_machine
    from common.validation import validate_profile_data, sanitize_login_credentials, ValidationError as ValidationErr
    from common.job_matcher import calculate_job_match_score, rank_jobs
    from database import (
        init_database, get_collection, create_session, get_active_session, delete_session, 
        cleanup_expired_sessions, create_user, get_user_by_email, save_resume, get_latest_resume, 
        cleanup_expired_resumes, save_profile, get_profile, delete_profile, save_application_state, 
        get_application_state, delete_application_state, save_statistics, get_statistics, 
        delete_statistics, delete_all_user_data, download_resume_from_gridfs, save_screenshot, 
        get_latest_screenshot, cleanup_expired_screenshots, run_cleanup_tasks, 
        start_cleanup_scheduler, stop_cleanup_scheduler
    )
except ImportError:
    print("Warning: Some common modules not available. Running in standalone mode.")

app = Flask(__name__)
CORS(app)
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    logger=True,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25,
)

# Rate limiting configuration
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "200 per hour"],
    storage_uri="memory://",
)

# Configuration
PROJECT_DIR = Path(__file__).parent.parent

# Use Render's persistent disk if available (paid tier), otherwise use local paths (free tier)
DATA_DIR = Path(os.environ.get('RENDER_DISK_MOUNT_PATH', PROJECT_DIR))

PROFILE_FILE = DATA_DIR / "profile.yaml"
SESSION_FILE = DATA_DIR / "session_naukri.json"
STATS_FILE = DATA_DIR / "application_stats.json"
LOG_FILE = DATA_DIR / "applications_log.csv"
RESUME_DIR = DATA_DIR / "resumes"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

# Create screenshots directory
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# HTTPS Configuration
ENABLE_HTTPS = os.environ.get('ENABLE_HTTPS', 'false').lower() == 'true'
SSL_CERT_DIR = os.environ.get('SSL_CERT_DIR', str(PROJECT_DIR / 'ssl_certs'))

# Create necessary directories
RESUME_DIR.mkdir(parents=True, exist_ok=True)

# Global automation state
automation_running = False
automation_thread = None
automation_process = None

# Initialize database on startup
try:
    init_database()
    # Start the cleanup scheduler
    start_cleanup_scheduler()
except Exception as e:
    print(f"Warning: Database initialization failed: {e}")

# User management (simplified - single user for now)
CURRENT_USER_ID = "default_user"  # Will be replaced with actual user authentication later


def cleanup_expired_sessions():
    """Delete expired sessions and associated files."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    now = datetime.now()
    
    # Find expired sessions
    cursor.execute('''
        SELECT id, session_file_path, browser_profile_path
        FROM naukri_sessions
        WHERE expires_at < ?
    ''', (now,))
    
    expired_sessions = cursor.fetchall()
    
    for session_id, session_file, browser_profile in expired_sessions:
        # Delete session file
        if session_file and Path(session_file).exists():
            try:
                Path(session_file).unlink()
            except Exception as e:
                print(f"Error deleting session file: {e}")
        
        # Delete browser profile
        if browser_profile and Path(browser_profile).exists():
            try:
                shutil.rmtree(browser_profile)
            except Exception as e:
                print(f"Error deleting browser profile: {e}")
    
    # Delete expired records from database
    cursor.execute('DELETE FROM naukri_sessions WHERE expires_at < ?', (now,))
    
    # Delete expired resumes
    cursor.execute('''
        SELECT id, file_path
        FROM resumes
        WHERE expires_at < ?
    ''', (now,))
    
    expired_resumes = cursor.fetchall()
    for resume_id, file_path in expired_resumes:
        if file_path and Path(file_path).exists():
            try:
                Path(file_path).unlink()
            except Exception as e:
                print(f"Error deleting resume file: {e}")
    
    cursor.execute('DELETE FROM resumes WHERE expires_at < ?', (now,))
    
    conn.commit()
    conn.close()
    
    if expired_sessions or expired_resumes:
        print(f"Cleaned up {len(expired_sessions)} expired sessions and {len(expired_resumes)} expired resumes")


def cleanup_worker():
    """Background worker to clean up expired sessions every hour."""
    while True:
        try:
            cleanup_expired_sessions()
        except Exception as e:
            print(f"Error in cleanup worker: {e}")
        time.sleep(3600)  # Run every hour


# Start cleanup worker
cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
cleanup_thread.start()


# Initialize database on startup
init_database()
cleanup_expired_sessions()


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/session/status', methods=['GET'])
def session_status():
    """Get current Naukri session status."""
    try:
        now = datetime.now()
        
        # Get active session for current user
        session = get_active_session(CURRENT_USER_ID)

        if session:
            session_id = session.get('session_id')
            created_at = session.get('created_at')
            expires_at = session.get('expires_at')
            status = session.get('status')
            
            # Calculate time remaining
            if expires_at:
                time_remaining = (expires_at - now).total_seconds()
            else:
                time_remaining = 0

            return jsonify({
                'success': True,
                'connected': status == 'connected',
                'session_id': session_id,
                'created_at': created_at,
                'expires_at': expires_at,
                'time_remaining_seconds': time_remaining,
                'time_remaining_hours': time_remaining / 3600
            })
        else:
            return jsonify({
                'success': True,
                'connected': False,
                'message': 'No active session'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/naukri/connect', methods=['POST'])
def connect_naukri():
    """Initiate Naukri connection flow - checks if session file exists."""
    try:
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        created_at = datetime.now()
        expires_at = created_at + timedelta(hours=12)

        # Check if session file already exists (from login_capture.py)
        if SESSION_FILE.exists():
            # Create session record in database
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO naukri_sessions (session_id, created_at, expires_at, status, session_file_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, created_at, expires_at, 'connected', str(SESSION_FILE)))
            conn.commit()
            conn.close()

            return jsonify({
                'success': True,
                'message': 'Naukri session connected successfully',
                'session_id': session_id
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No session file found. Please use the login form to connect your Naukri account.'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/naukri/login', methods=['POST'])
@limiter.limit("20 per hour")  # Increased limit for login attempts
def login_naukri():
    """Login to Naukri with credentials and create session."""
    try:
        data = request.json

        # Validate and sanitize credentials
        try:
            credentials = sanitize_login_credentials(data)
        except ValidationErr as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400

        email = credentials['email']
        password = credentials['password']

        # Use Playwright to automate login with human-like behavior
        from playwright.sync_api import sync_playwright
        import random
        import time

        with sync_playwright() as p:
            # Launch browser with realistic settings
            browser = p.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )

            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            page = context.new_page()

            # Navigate to login page with random delay
            page.goto('https://www.naukri.com/nlogin/login')
            time.sleep(random.uniform(1.5, 3.0))

            # Wait for login form to be visible
            page.wait_for_selector('input[placeholder*="Email"], input[placeholder*="email"], input[name*="email"], input[type="email"][placeholder]', timeout=10000)

            # Fill email with human-like typing - use more specific selectors
            email_selector = 'input[placeholder*="Email"], input[placeholder*="email"], input[name*="email"]'
            if page.locator(email_selector).count() > 0:
                page.fill(email_selector, email)
            else:
                # Fallback to type="email" if placeholder-based selector fails
                page.fill('input[type="email"]', email)
            time.sleep(random.uniform(0.5, 1.5))

            # Fill password with human-like typing
            password_selector = 'input[type="password"]'
            page.fill(password_selector, password)
            time.sleep(random.uniform(0.5, 1.5))

            # Click login button - try multiple selectors
            login_button_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Login")',
                'button:has-text("login")',
                '[data-testid="loginBtn"]',
                '.login-btn'
            ]
            for selector in login_button_selectors:
                if page.locator(selector).count() > 0:
                    page.click(selector)
                    break
            time.sleep(random.uniform(2.0, 4.0))

            # Wait for navigation or check if login successful
            try:
                page.wait_for_load_state('networkidle', timeout=10000)
            except:
                pass

            # Check if we're logged in (look for logout button or user profile)
            is_logged_in = False
            try:
                is_logged_in = page.locator('a[href*="logout"], .logout-btn, [data-testid="logout"]').count() > 0
                if not is_logged_in:
                    # Alternative check: look for logged-in indicators
                    is_logged_in = 'naukri.com' in page.url and '/nlogin/login' not in page.url
            except:
                # Fallback: check URL
                is_logged_in = '/nlogin/login' not in page.url

            if is_logged_in:
                # Save session
                context.storage_state(path=str(SESSION_FILE))
                browser.close()

                # Create session record in database
                session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                created_at = datetime.now()
                expires_at = created_at + timedelta(hours=12)

                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO naukri_sessions (session_id, created_at, expires_at, status, session_file_path)
                    VALUES (?, ?, ?, ?, ?)
                ''', (session_id, created_at, expires_at, 'connected', str(SESSION_FILE)))
                conn.commit()
                conn.close()

                return jsonify({
                    'success': True,
                    'message': 'Login successful! Session created.',
                    'session_id': session_id
                })
            else:
                browser.close()
                return jsonify({
                    'success': False,
                    'error': 'Login failed. Please check your credentials and try again.'
                }), 401

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Login failed: {str(e)}'
        }), 500


@app.route('/api/naukri/disconnect', methods=['POST'])
def disconnect_naukri():
    """Disconnect Naukri session and delete all user data."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get active session
        cursor.execute('''
            SELECT session_file_path, browser_profile_path
            FROM naukri_sessions
            WHERE status = 'connected'
            ORDER BY created_at DESC
            LIMIT 1
        ''')
        
        session = cursor.fetchone()
        
        if session:
            session_file, browser_profile = session
            
            # Delete session file
            if session_file and Path(session_file).exists():
                Path(session_file).unlink()
            
            # Delete browser profile
            if browser_profile and Path(browser_profile).exists():
                shutil.rmtree(browser_profile)
            
            # Delete main session file
            if SESSION_FILE.exists():
                SESSION_FILE.unlink()
        
        # Mark all sessions as disconnected
        cursor.execute('UPDATE naukri_sessions SET status = ? WHERE status = ?', ('disconnected', 'connected'))

        # Delete all resume records and files from backend/resumes
        cursor.execute('SELECT file_path FROM resumes')
        resumes = cursor.fetchall()
        for (file_path,) in resumes:
            if file_path and Path(file_path).exists():
                try:
                    Path(file_path).unlink()
                except Exception as e:
                    print(f"Error deleting resume file: {e}")

        # Delete all resume records from database
        cursor.execute('DELETE FROM resumes')

        # Delete all user records
        cursor.execute('DELETE FROM users')

        conn.commit()
        conn.close()

        # Delete backend/resumes directory (after closing database connection)
        backend_resumes_dir = PROJECT_DIR / 'backend' / 'resumes'
        if backend_resumes_dir.exists():
            try:
                shutil.rmtree(backend_resumes_dir)
            except Exception as e:
                print(f"Error deleting backend/resumes directory: {e}")
        
        # Delete profile.yaml (reset to empty)
        if PROFILE_FILE.exists():
            try:
                PROFILE_FILE.unlink()
                # Create empty profile file with null values
                empty_profile = {
                    'target_roles': None,
                    'skills': None,
                    'email': None,
                    'phone': None,
                    'location': None,
                    'preferred_locations': None,
                    'experience_years': None,
                    'notice_period': None,
                    'current_ctc': None,
                    'expected_ctc': None,
                    'additional_context': None,
                    'resume_filename': None,
                    'resume_file_name': None,
                    'full_name': None,
                    'current_city': None,
                    'linkedin': None,
                    'github': None,
                    'portfolio': None,
                    'total_experience_years': None
                }
                with open(PROFILE_FILE, 'w') as f:
                    yaml.dump(empty_profile, f, default_flow_style=False)
            except Exception as e:
                print(f"Error deleting profile.yaml: {e}")
        
        # Delete application history files
        app_log = PROJECT_DIR / 'applications_log.csv'
        app_stats = PROJECT_DIR / 'application_stats.json'
        app_state = PROJECT_DIR / 'application_state.json'
        
        for file in [app_log, app_stats, app_state]:
            if file.exists():
                try:
                    file.unlink()
                except Exception as e:
                    print(f"Error deleting {file.name}: {e}")
        
        # Delete screenshots directory
        screenshots_dir = PROJECT_DIR / 'screenshots'
        if screenshots_dir.exists():
            try:
                shutil.rmtree(screenshots_dir)
            except Exception as e:
                print(f"Error deleting screenshots directory: {e}")
        
        # Delete debug screenshots directory
        debug_screenshots_dir = PROJECT_DIR / 'debug_screenshots'
        if debug_screenshots_dir.exists():
            try:
                shutil.rmtree(debug_screenshots_dir)
            except Exception as e:
                print(f"Error deleting debug_screenshots directory: {e}")
        
        # Delete security events log
        security_events = PROJECT_DIR / 'security_events.jsonl'
        if security_events.exists():
            try:
                security_events.unlink()
            except Exception as e:
                print(f"Error deleting security_events.jsonl: {e}")
        
        # Delete learned answers file
        learned_answers = PROJECT_DIR / 'learned_answers.json'
        if learned_answers.exists():
            try:
                learned_answers.unlink()
            except Exception as e:
                print(f"Error deleting learned_answers.json: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Naukri session disconnected and all user data deleted'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get current profile configuration."""
    try:
        if PROFILE_FILE.exists():
            with open(PROFILE_FILE, 'r') as f:
                profile = yaml.safe_load(f)
                if profile is None:
                    profile = {}
            return jsonify({'success': True, 'profile': profile})
        else:
            # Return empty profile if file doesn't exist
            return jsonify({'success': True, 'profile': {}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/profile', methods=['POST'])
def update_profile():
    """Update profile configuration."""
    try:
        data = request.json

        # Validate and sanitize profile data
        try:
            validated_data = validate_profile_data(data)
        except ValidationErr as e:
            return jsonify({'success': False, 'error': str(e)}), 400

        # Load existing profile
        if PROFILE_FILE.exists():
            with open(PROFILE_FILE, 'r') as f:
                profile = yaml.safe_load(f) or {}
        else:
            profile = {}

        # Update with validated data
        profile.update(validated_data)

        # Save profile atomically
        temp_file = PROFILE_FILE.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            yaml.dump(profile, f, default_flow_style=False)
        temp_file.replace(PROFILE_FILE)

        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/resume/upload', methods=['POST'])
def upload_resume():
    """Upload resume file."""
    try:
        if 'resume' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})

        file = request.files['resume']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Allowed: PDF, DOC, DOCX'})

        # Ensure resumes directory exists
        RESUME_DIR.mkdir(parents=True, exist_ok=True)

        # Save resume
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        saved_filename = f"{timestamp}_{filename}"
        file_path = RESUME_DIR / saved_filename
        file.save(str(file_path))

        # Extract data from resume
        from common.resume_parser import parse_resume
        try:
            parsed_data = parse_resume(str(file_path))
        except Exception as parse_error:
            # If parsing fails, return the file path and error but still save the file
            return jsonify({
                'success': False,
                'error': f'Failed to parse resume: {str(parse_error)}. The file was saved but could not be extracted. This may be due to a password-protected PDF or corrupted file.'
            }), 500

        # Save to database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Create or get user (simplified - using single user for now)
        cursor.execute('INSERT OR IGNORE INTO users (email, created_at, updated_at) VALUES (?, ?, ?)',
                      ('user@example.com', datetime.now(), datetime.now()))
        user_id = cursor.lastrowid or cursor.execute('SELECT id FROM users LIMIT 1').fetchone()[0]

        # Store resume record
        expires_at = datetime.now() + timedelta(hours=12)
        cursor.execute('''
            INSERT INTO resumes (user_id, filename, original_filename, file_path, parsed_data, uploaded_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, saved_filename, filename, str(file_path), json.dumps(parsed_data), datetime.now(), expires_at))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Resume uploaded and parsed successfully',
            'resume_data': parsed_data,
            'file_path': str(file_path)
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/resume/approve', methods=['POST'])
def approve_resume_data():
    """Approve parsed resume data and sync with profile."""
    try:
        data = request.json
        # The frontend sends: { approved_data: {...}, resume_filename: "..." }
        resume_data = data.get('approved_data')
        resume_filename = data.get('resume_filename')

        print(f"=== RESUME APPROVE ===")
        print(f"Resume data: {resume_data}")
        print(f"Resume filename: {resume_filename}")

        if not resume_data:
            return jsonify({'success': False, 'error': 'No approved data provided'})

        # Load existing profile
        if PROFILE_FILE.exists():
            with open(PROFILE_FILE, 'r') as f:
                profile = yaml.safe_load(f) or {}
        else:
            profile = {}

        # Ensure required automation configuration fields exist
        required_config_fields = {
            'stop_after_n_applications': 6,
            'max_applications_per_day': 20,
            'max_applications_per_hour': 15,
            'max_pages_per_role': 5,
            'max_retries': 2,
            'pace_seconds_between_actions': 30,
            'job_freshness_days_phase1': 7,
            'job_freshness_days_phase2': 30,
            'title_exclude_keywords': ['senior', 'sr', 'sr.', 'lead', 'principal', 'staff', 'manager', 'architect', 'director', 'head', 'experienced', '2+ years', '2 years', '3+ years', '3 years', 'expert', 'specialist'],
            'browser_mode': 'minimized',
            'emergency_stop_enabled': True,
            'stop_on_authentication_error': True,
            'stop_on_captcha': True,
            'stop_on_rate_limit': True,
            'salary_floor_lpa': 2.5,
            'seniority_floor_years': 0,
            'seniority_ceiling_years': 1,
            'human_input_timeout_seconds': 120,
            'llm_data_sharing': False,
            'save_debug_artifacts': False,
            'role_required_keywords': {},
            'role_family_groups': {},
            'company_exclude': [],
            'company_include_only': [],
            'notice_period_days': 0,
            'currently_employed': False,
            'current_company': '',
            'current_role': '',
            'current_ctc_lpa': 0.0,
            'expected_ctc_lpa': 3.0,
            'relocate_cities': True,
            'willing_to_relocate': True,
            'night_shift_ok': False,
            'weekend_ok': False,
            'immediately_available': False,
        }

        # Add missing config fields without overwriting existing values
        for key, default_value in required_config_fields.items():
            if key not in profile:
                profile[key] = default_value

        print(f"Current profile keys: {list(profile.keys())}")
        print(f"Resume data keys: {list(resume_data.keys())}")

        # The actual data is nested inside approved_data key
        # Frontend sends: { approved_data: {full_name, email, ...}, resume_filename }
        if 'approved_data' in resume_data:
            # Unwrap the nested data
            resume_data_to_save = resume_data['approved_data']
        else:
            # Use the data directly if not nested
            resume_data_to_save = resume_data

        # Map resume parser fields to profile fields
        field_mapping = {
            'location': 'current_city',  # Map location to current_city
        }

        # Apply mapping and update profile
        for key, value in resume_data_to_save.items():
            mapped_key = field_mapping.get(key, key)
            profile[mapped_key] = value

        # Save resume filename if provided (save to both field names for compatibility)
        if resume_filename:
            profile['resume_filename'] = resume_filename
            profile['resume_file_name'] = resume_filename

        print(f"Updated profile keys: {list(profile.keys())}")
        print(f"Skills in profile: {profile.get('skills')}")
        print(f"Target roles in profile: {profile.get('target_roles')}")

        # Save profile atomically
        temp_file = PROFILE_FILE.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            yaml.dump(profile, f, default_flow_style=False)
        temp_file.replace(PROFILE_FILE)

        print("=== RESUME APPROVE SUCCESS ===")

        return jsonify({
            'success': True,
            'message': 'Resume data approved and profile updated'
        })
    except Exception as e:
        print(f"=== RESUME APPROVE ERROR: {e} ===")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/resume/status', methods=['GET'])
def get_resume_status():
    """Check if resume has been uploaded and profile is populated."""
    try:
        # Check if profile exists and has required fields
        if PROFILE_FILE.exists():
            with open(PROFILE_FILE, 'r') as f:
                profile = yaml.safe_load(f) or {}

            # Check for essential fields that indicate resume data
            # Only consider it has resume if skills is a non-empty list
            skills = profile.get('skills')
            has_resume_data = bool(
                skills and isinstance(skills, list) and len(skills) > 0
            )

            # Get resume filename (check both field names for compatibility)
            resume_filename = profile.get('resume_filename') or profile.get('resume_file_name')

            return jsonify({
                'success': True,
                'has_resume': has_resume_data,
                'profile_complete': has_resume_data,
                'profile': profile if has_resume_data else None,
                'resume_filename': resume_filename if has_resume_data else None
            })
        else:
            return jsonify({
                'success': True,
                'has_resume': False,
                'profile_complete': False,
                'profile': None,
                'resume_filename': None
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/api-keys', methods=['POST'])
def save_api_keys():
    """Save API keys to .env file."""
    try:
        data = request.json
        gemini_key = data.get('gemini_key')
        groq_key = data.get('groq_key')
        openrouter_key = data.get('openrouter_key')

        env_file = PROJECT_DIR / '.env'

        # Read existing .env file
        env_content = ""
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.read()

        # Update or add API keys
        lines = env_content.split('\n')
        updated_lines = []

        if gemini_key:
            updated_lines.append(f'GEMINI_API_KEY={gemini_key}')
        if groq_key:
            updated_lines.append(f'GROQ_API_KEY={groq_key}')
        if openrouter_key:
            updated_lines.append(f'OPENROUTER_API_KEY={openrouter_key}')

        # Keep other lines
        for line in lines:
            if line and not line.startswith('GEMINI_API_KEY=') and not line.startswith('GROQ_API_KEY=') and not line.startswith('OPENROUTER_API_KEY='):
                updated_lines.append(line)

        # Write back to .env
        with open(env_file, 'w') as f:
            f.write('\n'.join(updated_lines))

        # Reload environment variables
        os.environ['GEMINI_API_KEY'] = gemini_key or os.environ.get('GEMINI_API_KEY', '')
        if groq_key:
            os.environ['GROQ_API_KEY'] = groq_key
        if openrouter_key:
            os.environ['OPENROUTER_API_KEY'] = openrouter_key

        return jsonify({'success': True, 'message': 'API keys saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/api-keys', methods=['GET'])
def get_api_keys():
    """Get current API keys status (without exposing actual keys)."""
    try:
        gemini_key = os.getenv('GEMINI_API_KEY', '')
        groq_key = os.getenv('GROQ_API_KEY', '')
        openrouter_key = os.getenv('OPENROUTER_API_KEY', '')

        return jsonify({
            'success': True,
            'gemini_configured': bool(gemini_key and gemini_key != 'your-gemini-api-key-here'),
            'groq_configured': bool(groq_key and groq_key != 'your-groq-api-key-here'),
            'openrouter_configured': bool(openrouter_key and openrouter_key != 'your-openrouter-api-key-here')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get application statistics."""
    try:
        if STATS_FILE.exists():
            with open(STATS_FILE, 'r') as f:
                stats = json.load(f)
            return jsonify({'success': True, 'stats': stats})
        else:
            return jsonify({'success': False, 'error': 'Stats file not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/applications', methods=['GET'])
def get_applications():
    """Get application history from CSV log."""
    try:
        import csv
        applications = []

        if LOG_FILE.exists():
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    applications.append(row)

        # Sort by timestamp descending (newest first)
        applications.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return jsonify({'success': True, 'applications': applications})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/automation/start', methods=['POST'])
def start_automation():
    """Start the automation."""
    global automation_running, automation_process

    if automation_running:
        return jsonify({'success': False, 'error': 'Automation already running'})

    # Check if session file exists
    session_file = PROJECT_DIR / 'session_naukri.json'
    if not session_file.exists():
        return jsonify({'success': False, 'error': 'No active Naukri session. Please login first.'}), 400

    # Check if profile file exists
    profile_file = PROJECT_DIR / 'profile.yaml'
    if not profile_file.exists():
        return jsonify({'success': False, 'error': 'No profile configured. Please set up your profile first.'}), 400

    # Check if API key is configured (Gemini, Groq, or OpenRouter)
    gemini_key = os.getenv('GEMINI_API_KEY')
    groq_key = os.getenv('GROQ_API_KEY')
    openrouter_key = os.getenv('OPENROUTER_API_KEY')

    has_gemini = gemini_key and gemini_key != 'your-gemini-api-key-here'
    has_groq = groq_key and groq_key != 'your-groq-api-key-here'
    has_openrouter = openrouter_key and openrouter_key != 'your-openrouter-api-key-here'

    if not (has_gemini or has_groq or has_openrouter):
        return jsonify({
            'success': False,
            'error': 'No API key configured. Please set GEMINI_API_KEY, GROQ_API_KEY, or OPENROUTER_API_KEY in .env file or Settings page.'
        }), 400

    # Load profile to check dry_run mode
    try:
        with open(profile_file, 'r') as f:
            profile = yaml.safe_load(f) or {}
        if profile.get('dry_run', False):
            return jsonify({
                'success': False,
                'error': 'Dry-run mode is enabled. Please disable it in Settings or profile.yaml to apply to real jobs.'
            }), 400
    except Exception as e:
        print(f"Warning: Could not check dry_run mode: {e}")

    # Check if virtual environment Python exists
    venv_python = PROJECT_DIR / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = PROJECT_DIR / ".venv" / "bin" / "python"
    if not venv_python.exists():
        return jsonify({
            'success': False,
            'error': 'Virtual environment Python not found. Please ensure .venv is properly set up.'
        }), 400

    # Reset stats file before starting new run
    try:
        empty_stats = {
            "total_seen": 0,
            "total_qualified": 0,
            "total_filtered": 0,
            "total_applied": 0,
            "total_skipped": 0,
            "total_errors": 0,
            "total_uncertain": 0,
            "total_duplicates_skipped": 0,
            "total_security_stops": 0,
            "by_role": {},
            "by_company": {},
            "by_error_category": {},
            "by_skip_reason": {},
            "success_rate": 0
        }
        with open(STATS_FILE, 'w') as f:
            json.dump(empty_stats, f, indent=2)
        print("Stats reset for new run")
    except Exception as e:
        print(f"Warning: Could not reset stats file: {e}")

    # Reset application state file to clear old job records
    try:
        state_file = PROJECT_DIR / 'application_state.json'
        empty_state = {
            "last_updated": datetime.now().isoformat(),
            "records": []
        }
        with open(state_file, 'w') as f:
            json.dump(empty_state, f, indent=2)
        print("Application state reset for new run")
    except Exception as e:
        print(f"Warning: Could not reset application state file: {e}")

    try:
        automation_running = True

        # Run automation as subprocess using the virtual environment Python
        import subprocess
        import threading

        def stream_output(process):
            """Stream subprocess output to WebSocket clients."""
            try:
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    if line.strip():
                        broadcast_automation_progress(line.strip(), 0)
                        print(f"[STREAM] {line.strip()}")

                # Read any remaining stderr
                for line in process.stderr:
                    if line.strip():
                        broadcast_automation_progress(f"ERROR: {line.strip()}", 0)
                        print(f"[STREAM ERROR] {line.strip()}")
            except Exception as e:
                print(f"Error streaming output: {e}")
            finally:
                # Mark automation as stopped when process ends
                global automation_running
                automation_running = False
                broadcast_automation_status('stopped')

        automation_process = subprocess.Popen(
            [str(venv_python), 'naukri_apply.py'],
            cwd=str(PROJECT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'
        )

        # Start streaming thread
        stream_thread = threading.Thread(target=stream_output, args=(automation_process,))
        stream_thread.daemon = True
        stream_thread.start()

        return jsonify({'success': True, 'message': 'Automation started'})
    except Exception as e:
        automation_running = False
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/automation/stop', methods=['POST'])
def stop_automation():
    """Stop the automation."""
    global automation_running, automation_process
    
    if not automation_running:
        return jsonify({'success': False, 'error': 'Automation not running'})
    
    try:
        if automation_process:
            automation_process.terminate()
            automation_process.wait(timeout=5)
        
        automation_running = False
        automation_process = None
        
        return jsonify({'success': True, 'message': 'Automation stopped'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/automation/status', methods=['GET'])
def automation_status():
    """Get automation status."""
    return jsonify({
        'success': True,
        'running': automation_running
    })


@app.route('/api/session/cleanup', methods=['POST'])
def manual_cleanup():
    """Manually trigger cleanup of expired sessions, resumes, and screenshots."""
    try:
        # Run all cleanup tasks
        session_count = cleanup_expired_sessions()
        resume_count = cleanup_expired_resumes()
        screenshot_count = cleanup_expired_screenshots()

        return jsonify({
            'success': True,
            'cleaned_sessions': session_count,
            'cleaned_resumes': resume_count,
            'cleaned_screenshots': screenshot_count,
            'message': f'Cleaned {session_count} sessions, {resume_count} resumes, {screenshot_count} screenshots'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/screenshots/latest', methods=['GET'])
def get_latest_screenshot():
    """Get the latest live screenshot."""
    try:
        import glob
        screenshots = sorted(SCREENSHOTS_DIR.glob("live_*.png"), reverse=True)
        if screenshots:
            latest = screenshots[0]
            return send_file(str(latest), mimetype='image/png')
        else:
            # Return 200 with empty data instead of 404 to handle gracefully
            return jsonify({'success': True, 'available': False, 'message': 'No screenshots available yet - automation may not have started'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/screenshots/status', methods=['GET'])
def screenshot_status():
    """Check if screenshots are being generated."""
    try:
        import glob
        screenshots = list(SCREENSHOTS_DIR.glob("live_*.png"))
        has_screenshots = len(screenshots) > 0
        return jsonify({
            'success': True,
            'has_screenshots': has_screenshots,
            'count': len(screenshots)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/jobs/match', methods=['POST'])
def match_jobs():
    """Calculate match scores for jobs against user profile."""
    try:
        data = request.json
        jobs = data.get('jobs', [])

        # Load profile
        if PROFILE_FILE.exists():
            with open(PROFILE_FILE, 'r') as f:
                profile = yaml.safe_load(f) or {}
        else:
            return jsonify({'success': False, 'error': 'Profile not found'}), 404

        # Calculate match scores
        try:
            ranked_jobs = rank_jobs(profile, jobs)
            return jsonify({
                'success': True,
                'ranked_jobs': ranked_jobs
            })
        except NameError:
            # Fallback if job_matcher not available
            return jsonify({
                'success': False,
                'error': 'Job matching module not available'
            }), 501

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('connected', {'data': 'Connected to server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')


@socketio.on('subscribe_automation')
def handle_subscribe():
    """Subscribe to automation progress updates."""
    print('Client subscribed to automation updates')
    emit('subscribed', {'message': 'Subscribed to automation updates'})


def broadcast_automation_progress(message: str, progress: float):
    """Broadcast automation progress to all connected clients."""
    socketio.emit('automation_progress', {
        'message': message,
        'progress': progress,
        'timestamp': datetime.now().isoformat()
    })


def broadcast_automation_status(status: str):
    """Broadcast automation status change to all connected clients."""
    socketio.emit('automation_status', {
        'status': status,
        'timestamp': datetime.now().isoformat()
    })


def broadcast_stats_update(stats: dict):
    """Broadcast stats update to all connected clients."""
    socketio.emit('stats_update', {
        'stats': stats,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    # Get port from environment variable (Render/production) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Use debug mode only if explicitly enabled (not in production)
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

    # Register shutdown handler to stop scheduler
    import atexit
    atexit.register(stop_cleanup_scheduler)

    if ENABLE_HTTPS:
        # Ensure SSL certificates exist
        try:
            from ssl_config import ensure_ssl_certs
            cert_path, key_path = ensure_ssl_certs(SSL_CERT_DIR)
            print(f"Running with HTTPS on port {port}")
            socketio.run(app, debug=debug_mode, host='0.0.0.0', port=port, ssl_context=(cert_path, key_path))
        except ImportError:
            print("cryptography library not installed. Falling back to HTTP.")
            print("Install with: pip install cryptography")
            socketio.run(app, debug=debug_mode, host='0.0.0.0', port=port)
    else:
        print(f"Running with HTTP on port {port}")
        socketio.run(app, debug=debug_mode, host='0.0.0.0', port=port)
