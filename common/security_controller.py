"""
Centralized Security Controller

Provides unified security detection and fail-closed behavior for all browser actions.
This is the single source of truth for security event detection and response.
"""
import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class SecurityEventType(Enum):
    """Types of security events that require immediate run termination."""
    CAPTCHA = "captcha"
    VERIFY_HUMAN = "verify_human"
    UNUSUAL_ACTIVITY = "unusual_activity"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ACCOUNT_RESTRICTION = "account_restriction"
    TEMPORARY_BLOCK = "temporary_block"
    PERMANENT_BLOCK = "permanent_block"
    SECURITY_VERIFICATION = "security_verification"
    CHECKPOINT = "checkpoint"
    RATE_LIMIT = "rate_limit"
    HTTP_401 = "http_401"
    HTTP_403 = "http_403"
    HTTP_429 = "http_429"
    LOGIN_REDIRECT = "login_redirect"
    SESSION_EXPIRED = "session_expired"
    OTP_2FA_CHALLENGE = "otp_2fa_challenge"
    AUTHENTICATION_FAILURE = "authentication_failure"


class SecurityEvent:
    """Represents a detected security event."""
    
    def __init__(
        self,
        event_type: SecurityEventType,
        signal: str,
        job_id: Optional[str] = None,
        company: Optional[str] = None,
        url: Optional[str] = None,
        action: Optional[str] = None,
    ):
        self.event_type = event_type
        self.signal = signal
        self.job_id = job_id
        self.company = company
        self.url = url
        self.action = action
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for logging (no sensitive data)."""
        return {
            "timestamp": self.timestamp,
            "event": self.event_type.value,
            "signal": self.signal,
            "job_id": self.job_id,
            "company": self.company,
            "url_domain": self._extract_domain(self.url) if self.url else None,
            "action": self.action,
            "result": "RUN_STOPPED",
        }
    
    @staticmethod
    def _extract_domain(url: Optional[str]) -> Optional[str]:
        """Extract domain from URL for logging (no sensitive path data)."""
        if not url:
            return None
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return None


class SecurityController:
    """
    Centralized security controller for all browser actions.
    
    Detects security events and enforces fail-closed behavior:
    - STOP THE COMPLETE AUTOMATION RUN on serious security signals
    - Never retry security events
    - Log all security events
    - Provide clear reason for stop
    """
    
    # Stop phrases that indicate security events
    STOP_PHRASES = [
        "too many requests",
        "unusual activity",
        "verify you are human",
        "captcha",
        "temporarily blocked",
        "please try again later and reduce",
        "there was an error while processing your request",
        "security verification",
        "we've restricted",
        "account has been restricted",
        "your account has been suspended",
        "access denied",
        "forbidden",
        "rate limit",
    ]
    
    # URL patterns that indicate security events
    SECURITY_URL_PATTERNS = [
        "/checkpoint/",
        "/login",
        "/verify",
        "/security",
        "/unusual-activity",
        "/blocked",
    ]
    
    def __init__(self, log_file: str = "security_events.jsonl"):
        self.log_file = Path(log_file)
        self._emergency_stop_triggered = False
        self._emergency_stop_file = Path("STOP_AUTOMATION")
    
    def check_page_for_security_signals(
        self,
        page_text: str,
        page_url: str,
        job_id: Optional[str] = None,
        company: Optional[str] = None,
        action: Optional[str] = None,
    ) -> Optional[SecurityEvent]:
        """
        Check a page for security signals.
        
        Returns a SecurityEvent if one is detected, None otherwise.
        This is a detection-only method - it does NOT stop the run.
        Callers should handle the SecurityEvent appropriately.
        """
        page_text_lower = page_text.lower()
        
        # Check for stop phrases
        for phrase in self.STOP_PHRASES:
            if phrase in page_text_lower:
                # Determine event type based on phrase
                if "captcha" in phrase:
                    event_type = SecurityEventType.CAPTCHA
                elif "verify" in phrase or "human" in phrase:
                    event_type = SecurityEventType.VERIFY_HUMAN
                elif "unusual" in phrase or "suspicious" in phrase:
                    event_type = SecurityEventType.UNUSUAL_ACTIVITY
                elif "blocked" in phrase or "temporarily" in phrase:
                    event_type = SecurityEventType.TEMPORARY_BLOCK
                elif "restricted" in phrase or "suspended" in phrase:
                    event_type = SecurityEventType.ACCOUNT_RESTRICTION
                elif "rate limit" in phrase or "too many" in phrase:
                    event_type = SecurityEventType.RATE_LIMIT
                else:
                    event_type = SecurityEventType.SECURITY_VERIFICATION
                
                return SecurityEvent(
                    event_type=event_type,
                    signal=phrase,
                    job_id=job_id,
                    company=company,
                    url=page_url,
                    action=action,
                )
        
        # Check for security URL patterns
        page_url_lower = page_url.lower()
        for pattern in self.SECURITY_URL_PATTERNS:
            if pattern in page_url_lower:
                if "/checkpoint/" in pattern:
                    event_type = SecurityEventType.CHECKPOINT
                elif "/login" in pattern:
                    event_type = SecurityEventType.LOGIN_REDIRECT
                elif "/verify" in pattern:
                    event_type = SecurityEventType.SECURITY_VERIFICATION
                elif "/security" in pattern:
                    event_type = SecurityEventType.SECURITY_VERIFICATION
                elif "/blocked" in pattern:
                    event_type = SecurityEventType.TEMPORARY_BLOCK
                else:
                    event_type = SecurityEventType.SECURITY_VERIFICATION
                
                return SecurityEvent(
                    event_type=event_type,
                    signal=f"URL pattern: {pattern}",
                    job_id=job_id,
                    company=company,
                    url=page_url,
                    action=action,
                )
        
        return None
    
    def check_http_status_code(
        self,
        status_code: int,
        job_id: Optional[str] = None,
        company: Optional[str] = None,
        url: Optional[str] = None,
        action: Optional[str] = None,
    ) -> Optional[SecurityEvent]:
        """
        Check HTTP status code for security-related errors.
        
        Returns a SecurityEvent if one is detected, None otherwise.
        """
        if status_code == 401:
            return SecurityEvent(
                event_type=SecurityEventType.HTTP_401,
                signal=f"HTTP {status_code}",
                job_id=job_id,
                company=company,
                url=url,
                action=action,
            )
        elif status_code == 403:
            return SecurityEvent(
                event_type=SecurityEventType.HTTP_403,
                signal=f"HTTP {status_code}",
                job_id=job_id,
                company=company,
                url=url,
                action=action,
            )
        elif status_code == 429:
            return SecurityEvent(
                event_type=SecurityEventType.HTTP_429,
                signal=f"HTTP {status_code}",
                job_id=job_id,
                company=company,
                url=url,
                action=action,
            )
        
        return None
    
    def check_emergency_stop(self) -> bool:
        """
        Check if emergency stop has been triggered.
        
        Returns True if emergency stop is active, False otherwise.
        """
        if self._emergency_stop_triggered:
            return True
        
        if self._emergency_stop_file.exists():
            self._emergency_stop_triggered = True
            return True
        
        return False
    
    def trigger_emergency_stop(self, reason: str):
        """
        Trigger emergency stop by creating the STOP_AUTOMATION file.
        """
        self._emergency_stop_triggered = True
        try:
            self._emergency_stop_file.write_text(f"Emergency stop triggered: {reason}\nTimestamp: {datetime.now().isoformat()}\n")
        except Exception as e:
            print(f"Warning: Could not create emergency stop file: {e}")
    
    def clear_emergency_stop(self):
        """
        Clear emergency stop by removing the STOP_AUTOMATION file.
        """
        self._emergency_stop_triggered = False
        if self._emergency_stop_file.exists():
            try:
                self._emergency_stop_file.unlink()
            except Exception as e:
                print(f"Warning: Could not remove emergency stop file: {e}")
    
    def log_security_event(self, event: SecurityEvent):
        """
        Log a security event to the security events log file.
        
        Never logs sensitive data (passwords, cookies, tokens).
        """
        try:
            # Ensure log directory exists
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Append event as JSONL line
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event.to_dict()) + "\n")
        except Exception as e:
            print(f"Warning: Could not log security event: {e}")
    
    def is_security_event_retryable(self, event: SecurityEvent) -> bool:
        """
        Determine if a security event is retryable.
        
        By design, NO security events are retryable.
        This enforces fail-closed behavior.
        """
        return False
    
    def should_stop_run_for_event(self, event: SecurityEvent) -> bool:
        """
        Determine if a security event should stop the entire run.
        
        By design, ALL security events stop the run.
        This enforces fail-closed behavior.
        """
        return True


# Global security controller instance
_security_controller = None


def get_security_controller(log_file: str = "security_events.jsonl") -> SecurityController:
    """
    Get the global security controller instance.
    """
    global _security_controller
    if _security_controller is None:
        _security_controller = SecurityController(log_file)
    return _security_controller
