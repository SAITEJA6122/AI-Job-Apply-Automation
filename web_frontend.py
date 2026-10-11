"""
Web Frontend for Naukri Job Application Automation
Provides a simple web interface to:
- Upload resume and auto-extract data
- Configure profile (role, skills, experience)
- Start/stop automation
- View application statistics
"""

from flask import Flask, render_template, request, jsonify, send_file
import yaml
import os
import json
from datetime import datetime
import subprocess
import threading
import PyPDF2
import re
from common.export_utils import export_application_log, export_statistics

app = Flask(__name__)

# Configuration
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_FILE = os.path.join(PROJECT_DIR, 'profile.yaml')
STATS_FILE = os.path.join(PROJECT_DIR, 'application_stats.json')
LOG_FILE = os.path.join(PROJECT_DIR, 'applications_log.csv')

# Global automation state
automation_running = False
automation_thread = None


def extract_resume_data(resume_path):
    """Extract data from resume PDF"""
    try:
        with open(resume_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        
        # Extract skills (common tech keywords)
        tech_keywords = [
            'python', 'javascript', 'java', 'react', 'angular', 'vue', 'node',
            'django', 'flask', 'express', 'mongodb', 'postgresql', 'mysql',
            'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'html', 'css', 'typescript', 'redux', 'graphql', 'rest api',
            'sql', 'nosql', 'linux', 'ubuntu', 'windows', 'macos',
            'agile', 'scrum', 'jenkins', 'ci/cd', 'testing', 'unittest'
        ]
        
        found_skills = []
        text_lower = text.lower()
        for keyword in tech_keywords:
            if keyword in text_lower:
                found_skills.append(keyword.capitalize())
        
        # Extract experience (look for patterns like "X years experience")
        experience_match = re.search(r'(\d+)\s*(?:years?|yrs?)\s*(?:of)?\s*experience', text, re.IGNORECASE)
        experience_years = int(experience_match.group(1)) if experience_match else 0
        
        # Extract education
        education_keywords = ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'b.sc', 'm.sc', 'degree']
        education = ""
        for keyword in education_keywords:
            if keyword in text_lower:
                education = keyword.capitalize()
                break
        
        # Extract name (first capitalized word after common headers)
        name_match = re.search(r'(?:name|candidate|profile)[\s:]+([A-Z][a-zA-Z\s]+)', text, re.IGNORECASE)
        name = name_match.group(1).strip() if name_match else ""
        
        return {
            'skills': found_skills,
            'experience_years': experience_years,
            'education': education,
            'name': name,
            'full_text': text[:500]  # First 500 chars for context
        }
    except Exception as e:
        print(f"Error extracting resume data: {e}")
        return {
            'skills': [],
            'experience_years': 0,
            'education': '',
            'name': '',
            'full_text': ''
        }


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get current profile configuration"""
    try:
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, 'r') as f:
                profile = yaml.safe_load(f)
            return jsonify({'success': True, 'profile': profile})
        else:
            return jsonify({'success': False, 'error': 'Profile file not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/profile', methods=['POST'])
def update_profile():
    """Update profile configuration"""
    try:
        data = request.json
        
        # Load existing profile
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, 'r') as f:
                profile = yaml.safe_load(f)
        else:
            profile = {}
        
        # Update with new data
        profile.update(data)
        
        # Save profile
        with open(PROFILE_FILE, 'w') as f:
            yaml.dump(profile, f, default_flow_style=False)
        
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get application statistics"""
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                stats = json.load(f)
            return jsonify({'success': True, 'stats': stats})
        else:
            return jsonify({'success': False, 'error': 'Stats file not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/automation/start', methods=['POST'])
def start_automation():
    """Start the automation"""
    global automation_running, automation_thread
    
    if automation_running:
        return jsonify({'success': False, 'error': 'Automation already running'})
    
    try:
        automation_running = True
        
        # Run automation in background thread
        def run_automation():
            global automation_running
            try:
                subprocess.run(['python', 'naukri_apply.py'], 
                             cwd=PROJECT_DIR,
                             capture_output=True,
                             text=True)
            finally:
                automation_running = False
        
        automation_thread = threading.Thread(target=run_automation)
        automation_thread.daemon = True
        automation_thread.start()
        
        return jsonify({'success': True, 'message': 'Automation started'})
    except Exception as e:
        automation_running = False
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/automation/status', methods=['GET'])
def automation_status():
    """Get automation status"""
    return jsonify({
        'success': True,
        'running': automation_running
    })


@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    """Upload resume file and extract data"""
    try:
        if 'resume' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        # Save resume
        resume_path = os.path.join(PROJECT_DIR, file.filename)
        file.save(resume_path)
        
        # Extract data from resume
        resume_data = extract_resume_data(resume_path)
        
        # Update profile.yaml with resume filename and extracted data
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, 'r') as f:
                profile = yaml.safe_load(f)
        else:
            profile = {}
        
        profile['resume_file_name'] = file.filename
        profile['extracted_skills'] = resume_data['skills']
        profile['extracted_experience'] = resume_data['experience_years']
        profile['extracted_education'] = resume_data['education']
        profile['extracted_name'] = resume_data['name']
        
        with open(PROFILE_FILE, 'w') as f:
            yaml.dump(profile, f, default_flow_style=False)
        
        return jsonify({
            'success': True, 
            'message': 'Resume uploaded and data extracted successfully',
            'resume_data': resume_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/export/log', methods=['GET'])
def export_log():
    """Export application log to CSV or Excel"""
    try:
        export_format = request.args.get('format', 'csv')
        if export_format not in ['csv', 'excel']:
            return jsonify({'success': False, 'error': 'Invalid format. Use csv or excel'})
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if export_format == 'excel':
            output_file = os.path.join(PROJECT_DIR, f'applications_export_{timestamp}.xlsx')
        else:
            output_file = os.path.join(PROJECT_DIR, f'applications_export_{timestamp}.csv')
        
        # Export
        success = export_application_log(
            log_file=LOG_FILE,
            output_format=export_format,
            output_file=output_file
        )
        
        if success:
            return send_file(output_file, as_attachment=True)
        else:
            return jsonify({'success': False, 'error': 'Export failed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/export/stats', methods=['GET'])
def export_stats():
    """Export statistics to CSV or Excel"""
    try:
        export_format = request.args.get('format', 'csv')
        if export_format not in ['csv', 'excel']:
            return jsonify({'success': False, 'error': 'Invalid format. Use csv or excel'})
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if export_format == 'excel':
            output_file = os.path.join(PROJECT_DIR, f'statistics_export_{timestamp}.xlsx')
        else:
            output_file = os.path.join(PROJECT_DIR, f'statistics_export_{timestamp}.csv')
        
        # Export
        success = export_statistics(
            stats_file=STATS_FILE,
            output_format=export_format,
            output_file=output_file
        )
        
        if success:
            return send_file(output_file, as_attachment=True)
        else:
            return jsonify({'success': False, 'error': 'Export failed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(PROJECT_DIR, 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
