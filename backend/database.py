"""
MongoDB Database Setup and Models with GridFS
Handles all database operations for Naukri Job Automation
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from gridfs import GridFS
import json
import threading

# MongoDB Configuration
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
DATABASE_NAME = os.environ.get('MONGODB_DATABASE', 'naukri_automation')

# Initialize MongoDB client
try:
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    print(f"Connected to MongoDB: {DATABASE_NAME}")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    client = None
    db = None

# Initialize GridFS for file storage (resumes and screenshots)
if db is not None:
    resumes_fs = GridFS(db, collection='resumes')
    screenshots_fs = GridFS(db, collection='screenshots')
else:
    resumes_fs = None
    screenshots_fs = None


# ==================== MongoDB Models ====================

def get_collection(collection_name: str):
    """Get a MongoDB collection."""
    if db is None:
        raise RuntimeError("Database not connected")
    return db[collection_name]


def create_indexes():
    """Create indexes for better query performance."""
    if db is None:
        return

    # Sessions index
    db.naukri_sessions.create_index([("session_id", ASCENDING)], unique=True)
    db.naukri_sessions.create_index([("expires_at", DESCENDING)])
    db.naukri_sessions.create_index([("user_id", ASCENDING)])

    # Users index
    db.users.create_index([("email", ASCENDING)], unique=True)

    # Resumes index
    db.resumes.create_index([("user_id", ASCENDING)])
    db.resumes.create_index([("expires_at", DESCENDING)])

    # Screenshots index
    db.screenshots.create_index([("user_id", ASCENDING)])
    db.screenshots.create_index([("expires_at", DESCENDING)])
    db.screenshots.create_index([("created_at", DESCENDING)])

    # GridFS files indexes (automatically created by GridFS)
    db['resumes.files'].create_index([("expires_at", DESCENDING)])
    db['screenshots.files'].create_index([("expires_at", DESCENDING)])

    print("MongoDB indexes created successfully")


# ==================== Session Operations ====================

def create_session(session_id: str, user_id: str, expires_at: datetime, 
                  status: str = 'connected', session_file_path: str = None,
                  browser_profile_path: str = None) -> str:
    """Create a new Naukri session."""
    collection = get_collection('naukri_sessions')
    
    session_doc = {
        'session_id': session_id,
        'user_id': user_id,
        'created_at': datetime.now(),
        'expires_at': expires_at,
        'status': status,
        'session_file_path': session_file_path,
        'browser_profile_path': browser_profile_path
    }
    
    try:
        result = collection.insert_one(session_doc)
        return str(result.inserted_id)
    except DuplicateKeyError:
        collection.update_one(
            {'session_id': session_id},
            {'$set': session_doc}
        )
        return session_id


def get_active_session(user_id: str) -> Optional[Dict]:
    """Get the active session for a user."""
    collection = get_collection('naukri_sessions')
    
    now = datetime.now()
    session = collection.find_one({
        'user_id': user_id,
        'expires_at': {'$gt': now},
        'status': 'connected'
    })
    
    return session


def delete_session(session_id: str) -> bool:
    """Delete a session by ID."""
    collection = get_collection('naukri_sessions')
    result = collection.delete_one({'session_id': session_id})
    return result.deleted_count > 0


def cleanup_expired_sessions() -> int:
    """Delete expired sessions and return count."""
    collection = get_collection('naukri_sessions')
    
    now = datetime.now()
    result = collection.delete_many({'expires_at': {'$lt': now}})
    
    return result.deleted_count


# ==================== User Operations ====================

def create_user(email: str) -> str:
    """Create a new user."""
    collection = get_collection('users')
    
    user_doc = {
        'email': email,
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    try:
        result = collection.insert_one(user_doc)
        return str(result.inserted_id)
    except DuplicateKeyError:
        # User already exists
        user = collection.find_one({'email': email})
        return str(user['_id'])


def get_user_by_email(email: str) -> Optional[Dict]:
    """Get a user by email."""
    collection = get_collection('users')
    return collection.find_one({'email': email})


def update_user_timestamp(user_id: str):
    """Update user's last updated timestamp."""
    collection = get_collection('users')
    collection.update_one(
        {'_id': user_id},
        {'$set': {'updated_at': datetime.now()}}
    )


# ==================== Resume Operations ====================

def save_resume(user_id: str, filename: str, original_filename: str,
                file_path: str, parsed_data: Dict, expires_at: datetime) -> str:
    """Save resume file to GridFS and metadata to MongoDB."""
    # Upload file to GridFS
    file_id = upload_file_to_gridfs(file_path, filename, 'resumes', expires_at)
    
    if file_id is None:
        raise RuntimeError("Failed to upload resume to GridFS")
    
    # Save metadata
    collection = get_collection('resumes')
    
    resume_doc = {
        'user_id': user_id,
        'filename': filename,
        'original_filename': original_filename,
        'file_id': file_id,
        'parsed_data': parsed_data,
        'uploaded_at': datetime.now(),
        'expires_at': expires_at
    }
    
    result = collection.insert_one(resume_doc)
    return str(result.inserted_id)


def get_latest_resume(user_id: str) -> Optional[Dict]:
    """Get the latest resume for a user."""
    collection = get_collection('resumes')
    
    now = datetime.now()
    resume = collection.find_one({
        'user_id': user_id,
        'expires_at': {'$gt': now}
    }, sort=[('uploaded_at', DESCENDING)])
    
    return resume


def download_resume_from_gridfs(file_id: str, local_path: str) -> bool:
    """Download resume file from GridFS."""
    return download_file_from_gridfs(file_id, local_path, 'resumes')


def cleanup_expired_resumes() -> int:
    """Delete expired resume records and files, return count."""
    collection = get_collection('resumes')
    
    now = datetime.now()
    
    # Get expired resumes
    expired_resumes = collection.find({'expires_at': {'$lt': now}})
    count = 0
    
    for resume in expired_resumes:
        # Delete file from GridFS
        if 'file_id' in resume:
            delete_file_from_gridfs(resume['file_id'], 'resumes')
        count += 1
    
    # Delete records
    result = collection.delete_many({'expires_at': {'$lt': now}})
    
    # Also cleanup GridFS orphaned files
    cleanup_expired_gridfs_files('resumes')
    
    return count


def save_screenshot(user_id: str, file_path: str, filename: str, expires_at: datetime) -> Optional[str]:
    """Save screenshot to GridFS."""
    file_id = upload_file_to_gridfs(file_path, filename, 'screenshots', expires_at)
    
    if file_id is None:
        return None
    
    # Save metadata
    collection = get_collection('screenshots')
    
    screenshot_doc = {
        'user_id': user_id,
        'file_id': file_id,
        'filename': filename,
        'created_at': datetime.now(),
        'expires_at': expires_at
    }
    
    result = collection.insert_one(screenshot_doc)
    return str(result.inserted_id)


def get_latest_screenshot(user_id: str) -> Optional[Dict]:
    """Get the latest screenshot for a user."""
    collection = get_collection('screenshots')
    
    now = datetime.now()
    screenshot = collection.find_one({
        'user_id': user_id,
        'expires_at': {'$gt': now}
    }, sort=[('created_at', DESCENDING)])
    
    return screenshot


def cleanup_expired_screenshots() -> int:
    """Delete expired screenshot records and files, return count."""
    collection = get_collection('screenshots')
    
    now = datetime.now()
    
    # Get expired screenshots
    expired_screenshots = collection.find({'expires_at': {'$lt': now}})
    count = 0
    
    for screenshot in expired_screenshots:
        # Delete file from GridFS
        if 'file_id' in screenshot:
            delete_file_from_gridfs(screenshot['file_id'], 'screenshots')
        count += 1
    
    # Delete records
    result = collection.delete_many({'expires_at': {'$lt': now}})
    
    # Also cleanup GridFS orphaned files
    cleanup_expired_gridfs_files('screenshots')
    
    return count


# ==================== Profile Operations ====================

def save_profile(user_id: str, profile_data: Dict) -> bool:
    """Save user profile data."""
    collection = get_collection('profiles')
    
    profile_doc = {
        'user_id': user_id,
        'profile_data': profile_data,
        'updated_at': datetime.now()
    }
    
    collection.update_one(
        {'user_id': user_id},
        {'$set': profile_doc},
        upsert=True
    )
    
    return True


def get_profile(user_id: str) -> Optional[Dict]:
    """Get user profile data."""
    collection = get_collection('profiles')
    profile = collection.find_one({'user_id': user_id})
    
    if profile:
        return profile.get('profile_data')
    return None


def delete_profile(user_id: str) -> bool:
    """Delete user profile."""
    collection = get_collection('profiles')
    result = collection.delete_one({'user_id': user_id})
    return result.deleted_count > 0


# ==================== Application State Operations ====================

def save_application_state(user_id: str, application_state: Dict) -> bool:
    """Save application state."""
    collection = get_collection('application_states')
    
    state_doc = {
        'user_id': user_id,
        'state_data': application_state,
        'updated_at': datetime.now()
    }
    
    collection.update_one(
        {'user_id': user_id},
        {'$set': state_doc},
        upsert=True
    )
    
    return True


def get_application_state(user_id: str) -> Optional[Dict]:
    """Get application state."""
    collection = get_collection('application_states')
    state = collection.find_one({'user_id': user_id})
    
    if state:
        return state.get('state_data')
    return None


def delete_application_state(user_id: str) -> bool:
    """Delete application state."""
    collection = get_collection('application_states')
    result = collection.delete_one({'user_id': user_id})
    return result.deleted_count > 0


# ==================== Statistics Operations ====================

def save_statistics(user_id: str, stats: Dict) -> bool:
    """Save application statistics."""
    collection = get_collection('statistics')
    
    stats_doc = {
        'user_id': user_id,
        'stats_data': stats,
        'updated_at': datetime.now()
    }
    
    collection.update_one(
        {'user_id': user_id},
        {'$set': stats_doc},
        upsert=True
    )
    
    return True


def get_statistics(user_id: str) -> Optional[Dict]:
    """Get application statistics."""
    collection = get_collection('statistics')
    stats = collection.find_one({'user_id': user_id})
    
    if stats:
        return stats.get('stats_data')
    return None


def delete_statistics(user_id: str) -> bool:
    """Delete statistics."""
    collection = get_collection('statistics')
    result = collection.delete_one({'user_id': user_id})
    return result.deleted_count > 0


# ==================== GridFS File Operations ====================

def upload_file_to_gridfs(file_path: str, filename: str, collection: str = 'resumes', expires_at: datetime = None) -> Optional[str]:
    """Upload a file to MongoDB GridFS."""
    if db is None:
        print("Database not connected")
        return None
    
    try:
        fs = resumes_fs if collection == 'resumes' else screenshots_fs
        
        with open(file_path, 'rb') as f:
            file_id = fs.put(
                f,
                filename=filename,
                expires_at=expires_at,
                uploaded_at=datetime.now()
            )
        
        print(f"Uploaded {filename} to GridFS: {collection}")
        return str(file_id)
    except Exception as e:
        print(f"Failed to upload to GridFS: {e}")
        return None


def download_file_from_gridfs(file_id: str, local_path: str, collection: str = 'resumes') -> bool:
    """Download a file from MongoDB GridFS."""
    if db is None:
        print("Database not connected")
        return False
    
    try:
        fs = resumes_fs if collection == 'resumes' else screenshots_fs
        grid_out = fs.get(file_id)
        
        with open(local_path, 'wb') as f:
            f.write(grid_out.read())
        
        print(f"Downloaded {file_id} from GridFS to {local_path}")
        return True
    except Exception as e:
        print(f"Failed to download from GridFS: {e}")
        return False


def delete_file_from_gridfs(file_id: str, collection: str = 'resumes') -> bool:
    """Delete a file from MongoDB GridFS."""
    if db is None:
        print("Database not connected")
        return False
    
    try:
        fs = resumes_fs if collection == 'resumes' else screenshots_fs
        fs.delete(file_id)
        print(f"Deleted {file_id} from GridFS: {collection}")
        return True
    except Exception as e:
        print(f"Failed to delete from GridFS: {e}")
        return False


def cleanup_expired_gridfs_files(collection: str = 'resumes') -> int:
    """Delete expired files from GridFS and return count."""
    if db is None:
        return 0
    
    try:
        fs = resumes_fs if collection == 'resumes' else screenshots_fs
        now = datetime.now()
        
        # Find all files with expires_at in the past
        # GridFS stores metadata in .files collection
        files_collection = db[f'{collection}.files']
        
        expired_files = files_collection.find({'expires_at': {'$lt': now}})
        count = 0
        
        for file_doc in expired_files:
            try:
                fs.delete(file_doc['_id'])
                count += 1
            except Exception as e:
                print(f"Error deleting file {file_doc['_id']}: {e}")
        
        print(f"Cleaned up {count} expired files from {collection}")
        return count
    except Exception as e:
        print(f"Failed to cleanup expired files: {e}")
        return 0


# ==================== User Data Cleanup ====================

def delete_all_user_data(user_id: str) -> bool:
    """Delete all data for a user (used on disconnect)."""
    if db is None:
        return False
    
    # Delete sessions
    db.naukri_sessions.delete_many({'user_id': user_id})
    
    # Delete profile
    delete_profile(user_id)
    
    # Delete application state
    delete_application_state(user_id)
    
    # Delete statistics
    delete_statistics(user_id)
    
    # Delete resumes and files from GridFS
    resumes = db.resumes.find({'user_id': user_id})
    for resume in resumes:
        if 'file_id' in resume:
            delete_file_from_gridfs(resume['file_id'], 'resumes')
    db.resumes.delete_many({'user_id': user_id})
    
    # Delete screenshots and files from GridFS
    screenshots = db.screenshots.find({'user_id': user_id})
    for screenshot in screenshots:
        if 'file_id' in screenshot:
            delete_file_from_gridfs(screenshot['file_id'], 'screenshots')
    db.screenshots.delete_many({'user_id': user_id})
    
    print(f"Deleted all data for user: {user_id}")
    return True


# ==================== Initialization ====================

def init_database():
    """Initialize database and create indexes."""
    if db is None:
        print("Database not connected - skipping initialization")
        return False
    
    try:
        create_indexes()
        print("Database initialized successfully")
        return True
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        return False


def run_cleanup_tasks():
    """Run all cleanup tasks (expired sessions, resumes, screenshots)."""
    if db is None:
        return
    
    try:
        # Cleanup expired sessions
        session_count = cleanup_expired_sessions()
        
        # Cleanup expired resumes
        resume_count = cleanup_expired_resumes()
        
        # Cleanup expired screenshots
        screenshot_count = cleanup_expired_screenshots()
        
        print(f"[{datetime.now()}] Cleanup complete: {session_count} sessions, {resume_count} resumes, {screenshot_count} screenshots")
    except Exception as e:
        print(f"[{datetime.now()}] Cleanup failed: {e}")


# ==================== Scheduled Cleanup ====================

_scheduler = None
_scheduler_thread = None


def start_cleanup_scheduler():
    """Start the APScheduler for daily cleanup at 9 AM."""
    global _scheduler, _scheduler_thread
    
    if db is None:
        print("Database not connected - scheduler not started")
        return False
    
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        
        _scheduler = BackgroundScheduler(timezone='UTC')
        
        # Schedule cleanup every day at 9 AM UTC
        _scheduler.add_job(
            run_cleanup_tasks,
            trigger=CronTrigger(hour=9, minute=0),
            id='daily_cleanup',
            name='Daily cleanup at 9 AM UTC',
            replace_existing=True
        )
        
        _scheduler.start()
        print(f"[{datetime.now()}] Started cleanup scheduler - daily cleanup at 9 AM UTC")
        return True
    except ImportError:
        print("APScheduler not installed - cleanup will be manual only")
        return False
    except Exception as e:
        print(f"Failed to start scheduler: {e}")
        return False


def stop_cleanup_scheduler():
    """Stop the cleanup scheduler."""
    global _scheduler
    
    if _scheduler:
        _scheduler.shutdown()
        _scheduler = None
        print(f"[{datetime.now()}] Stopped cleanup scheduler")
