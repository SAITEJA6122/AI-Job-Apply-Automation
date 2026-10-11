"""
Notification System

Sends email notifications for job application events.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, List
import os
from pathlib import Path


class NotificationService:
    """Service for sending email notifications."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize notification service.
        
        Args:
            config: Dictionary with email configuration:
                - smtp_server: SMTP server address
                - smtp_port: SMTP port (default 587)
                - smtp_username: SMTP username
                - smtp_password: SMTP password
                - from_email: Sender email address
                - to_email: Recipient email address
        """
        self.config = config or {}
        self.enabled = bool(config and config.get('smtp_server'))
    
    def send_application_summary(
        self,
        total_applied: int,
        total_skipped: int,
        total_errors: int,
        success_rate: float,
        duration_seconds: float,
        jobs_by_role: Dict[str, Dict[str, int]],
    ) -> bool:
        """
        Send email summary after job application run.
        
        Args:
            total_applied: Number of jobs applied to
            total_skipped: Number of jobs skipped
            total_errors: Number of errors encountered
            success_rate: Success rate percentage
            duration_seconds: Duration of the run in seconds
            jobs_by_role: Dictionary of job statistics by role
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            print("Notifications disabled - no SMTP configuration")
            return False
        
        try:
            subject = f"🚀 Job Application Summary - {total_applied} Applications Submitted"
            
            # Build email body
            body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #667eea;">Job Application Run Summary</h2>
        
        <div style="background: #f5f7fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Overall Statistics</h3>
            <p><strong>Total Applied:</strong> {total_applied}</p>
            <p><strong>Total Skipped:</strong> {total_skipped}</p>
            <p><strong>Total Errors:</strong> {total_errors}</p>
            <p><strong>Success Rate:</strong> {success_rate:.1f}%</p>
            <p><strong>Duration:</strong> {duration_seconds:.1f} seconds</p>
        </div>
        
        <div style="background: #f5f7fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Jobs by Role</h3>
"""
            
            for role, stats in jobs_by_role.items():
                body += f"""
            <p><strong>{role}:</strong> 
               Seen: {stats.get('seen', 0)}, 
               Qualified: {stats.get('qualified', 0)}, 
               Applied: {stats.get('applied', 0)}, 
               Skipped: {stats.get('skipped', 0)}</p>
"""
            
            body += """
        </div>
        
        <p style="color: #666; font-size: 14px;">
            This is an automated email from the Naukri Job Automation System.
        </p>
    </div>
</body>
</html>
"""
            
            return self._send_email(subject, body, html=True)
            
        except Exception as e:
            print(f"Error sending application summary email: {e}")
            return False
    
    def send_error_alert(self, error_message: str, context: Optional[Dict] = None) -> bool:
        """
        Send email alert for critical errors.
        
        Args:
            error_message: Error message
            context: Additional context about the error
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            subject = "⚠️ Critical Error - Job Automation"
            
            body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #e74c3c;">Critical Error Alert</h2>
        
        <div style="background: #fee; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #e74c3c;">
            <p><strong>Error:</strong> {error_message}</p>
        </div>
"""
            
            if context:
                body += """
        <div style="background: #f5f7fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Context</h3>
"""
                for key, value in context.items():
                    body += f"<p><strong>{key}:</strong> {value}</p>"
                body += """
        </div>
"""
            
            body += """
        <p style="color: #666; font-size: 14px;">
            This is an automated email from the Naukri Job Automation System.
        </p>
    </div>
</body>
</html>
"""
            
            return self._send_email(subject, body, html=True)
            
        except Exception as e:
            print(f"Error sending error alert email: {e}")
            return False
    
    def _send_email(self, subject: str, body: str, html: bool = False) -> bool:
        """
        Send email using SMTP.
        
        Args:
            subject: Email subject
            body: Email body
            html: Whether body is HTML
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.get('from_email')
            msg['To'] = self.config.get('to_email')
            
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            smtp_server = self.config.get('smtp_server')
            smtp_port = self.config.get('smtp_port', 587)
            smtp_username = self.config.get('smtp_username')
            smtp_password = self.config.get('smtp_password')
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            print(f"Email sent successfully: {subject}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False


def get_notification_service() -> NotificationService:
    """
    Get notification service with configuration from environment variables.
    
    Environment variables:
        SMTP_SERVER: SMTP server address
        SMTP_PORT: SMTP port (default 587)
        SMTP_USERNAME: SMTP username
        SMTP_PASSWORD: SMTP password
        NOTIFICATION_FROM_EMAIL: Sender email
        NOTIFICATION_TO_EMAIL: Recipient email
    
    Returns:
        NotificationService instance
    """
    config = {
        'smtp_server': os.getenv('SMTP_SERVER'),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'smtp_username': os.getenv('SMTP_USERNAME'),
        'smtp_password': os.getenv('SMTP_PASSWORD'),
        'from_email': os.getenv('NOTIFICATION_FROM_EMAIL'),
        'to_email': os.getenv('NOTIFICATION_TO_EMAIL'),
    }
    
    # Only enable if all required fields are present
    if all(config.values()):
        return NotificationService(config)
    else:
        print("Email notifications disabled - missing SMTP configuration")
        return NotificationService(None)
