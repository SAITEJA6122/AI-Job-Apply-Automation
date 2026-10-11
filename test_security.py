"""
Security Tests

Tests for security controller, state machine, limiter, and other security features.
"""
import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta

from common.security_controller import (
    SecurityController,
    SecurityEventType,
    SecurityEvent,
)
from common.application_state import (
    ApplicationStateMachine,
    ApplicationRecord,
    ApplicationState,
)
from common.safety_config import SafetyConfig
from common.retry_handler import RetryHandler
from common.application_limiter import ApplicationLimiter


class TestSecurityController(unittest.TestCase):
    """Test security controller detection and fail-closed behavior."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = Path(self.temp_dir) / "security_events.jsonl"
        self.controller = SecurityController(str(self.log_file))
    
    def test_captcha_detection(self):
        """Test CAPTCHA detection."""
        page_text = "Please complete the captcha to continue"
        event = self.controller.check_page_for_security_signals(
            page_text=page_text,
            page_url="https://www.naukri.com/jobs",
        )
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, SecurityEventType.CAPTCHA)
    
    def test_unusual_activity_detection(self):
        """Test unusual activity detection."""
        page_text = "We detected unusual activity on your account"
        event = self.controller.check_page_for_security_signals(
            page_text=page_text,
            page_url="https://www.naukri.com/jobs",
        )
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, SecurityEventType.UNUSUAL_ACTIVITY)
    
    def test_rate_limit_detection(self):
        """Test rate limit detection."""
        page_text = "Too many requests. Please try again later."
        event = self.controller.check_page_for_security_signals(
            page_text=page_text,
            page_url="https://www.naukri.com/jobs",
        )
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, SecurityEventType.RATE_LIMIT)
    
    def test_login_redirect_detection(self):
        """Test login redirect detection."""
        page_text = "Welcome to Naukri"
        page_url = "https://www.naukri.com/nlogin/login"
        event = self.controller.check_page_for_security_signals(
            page_text=page_text,
            page_url=page_url,
        )
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, SecurityEventType.LOGIN_REDIRECT)
    
    def test_checkpoint_detection(self):
        """Test checkpoint detection."""
        page_text = "Welcome to Naukri"
        page_url = "https://www.naukri.com/checkpoint/verify"
        event = self.controller.check_page_for_security_signals(
            page_text=page_text,
            page_url=page_url,
        )
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, SecurityEventType.CHECKPOINT)
    
    def test_http_401_detection(self):
        """Test HTTP 401 detection."""
        event = self.controller.check_http_status_code(
            status_code=401,
            url="https://www.naukri.com/jobs",
        )
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, SecurityEventType.HTTP_401)
    
    def test_http_403_detection(self):
        """Test HTTP 403 detection."""
        event = self.controller.check_http_status_code(
            status_code=403,
            url="https://www.naukri.com/jobs",
        )
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, SecurityEventType.HTTP_403)
    
    def test_http_429_detection(self):
        """Test HTTP 429 detection."""
        event = self.controller.check_http_status_code(
            status_code=429,
            url="https://www.naukri.com/jobs",
        )
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, SecurityEventType.HTTP_429)
    
    def test_security_event_not_retryable(self):
        """Test that security events are never retryable."""
        event = SecurityEvent(
            event_type=SecurityEventType.CAPTCHA,
            signal="captcha",
        )
        self.assertFalse(self.controller.is_security_event_retryable(event))
    
    def test_security_event_stops_run(self):
        """Test that security events stop the run."""
        event = SecurityEvent(
            event_type=SecurityEventType.CAPTCHA,
            signal="captcha",
        )
        self.assertTrue(self.controller.should_stop_run_for_event(event))
    
    def test_emergency_stop(self):
        """Test emergency stop functionality."""
        self.assertFalse(self.controller.check_emergency_stop())
        self.controller.trigger_emergency_stop("Test stop")
        self.assertTrue(self.controller.check_emergency_stop())
        self.controller.clear_emergency_stop()
        self.assertFalse(self.controller.check_emergency_stop())
    
    def test_security_event_logging(self):
        """Test security event logging."""
        event = SecurityEvent(
            event_type=SecurityEventType.CAPTCHA,
            signal="captcha",
            job_id="12345",
            company="Test Company",
            url="https://www.naukri.com/jobs/12345",
            action="apply",
        )
        self.controller.log_security_event(event)
        
        # Verify log file was created
        self.assertTrue(self.log_file.exists())
        
        # Verify log content
        with open(self.log_file, "r") as f:
            log_line = f.readline()
            log_data = json.loads(log_line)
            self.assertEqual(log_data["event"], "captcha")
            self.assertEqual(log_data["job_id"], "12345")
            self.assertEqual(log_data["company"], "Test Company")
            # Verify no sensitive data in log
            self.assertNotIn("password", json.dumps(log_data).lower())
            self.assertNotIn("cookie", json.dumps(log_data).lower())


class TestApplicationStateMachine(unittest.TestCase):
    """Test application state machine and crash recovery."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = Path(self.temp_dir) / "application_state.json"
        self.state_machine = ApplicationStateMachine(str(self.state_file))
    
    def test_valid_state_transitions(self):
        """Test valid state transitions."""
        record = self.state_machine.create_record(
            job_id="12345",
            job_url="https://www.naukri.com/jobs/12345",
            title="Test Job",
            company="Test Company",
        )
        self.assertEqual(record.state, ApplicationState.DISCOVERED)
        
        # Valid transition
        self.state_machine.transition_record("12345", ApplicationState.FILTERED)
        record = self.state_machine.get_record("12345")
        self.assertEqual(record.state, ApplicationState.FILTERED)
    
    def test_invalid_state_transition(self):
        """Test invalid state transitions."""
        record = self.state_machine.create_record(
            job_id="12345",
            job_url="https://www.naukri.com/jobs/12345",
            title="Test Job",
            company="Test Company",
        )
        
        # Invalid transition: DISCOVERED -> SUBMITTED
        success = self.state_machine.transition_record("12345", ApplicationState.SUBMITTED)
        self.assertFalse(success)
    
    def test_uncertain_cannot_apply_again(self):
        """Test that UNCERTAIN state cannot transition to APPLY_STARTED."""
        record = self.state_machine.create_record(
            job_id="12345",
            job_url="https://www.naukri.com/jobs/12345",
            title="Test Job",
            company="Test Company",
        )
        
        # Transition to UNCERTAIN
        self.state_machine.transition_record("12345", ApplicationState.UNCERTAIN)
        
        # Try to transition to APPLY_STARTED (should fail)
        success = self.state_machine.transition_record("12345", ApplicationState.APPLY_STARTED)
        self.assertFalse(success)
    
    def test_security_stop_cannot_apply_again(self):
        """Test that SECURITY_STOP state cannot transition to APPLY_STARTED."""
        record = self.state_machine.create_record(
            job_id="12345",
            job_url="https://www.naukri.com/jobs/12345",
            title="Test Job",
            company="Test Company",
        )
        
        # Transition to SECURITY_STOP
        self.state_machine.transition_record("12345", ApplicationState.SECURITY_STOP)
        
        # Try to transition to APPLY_STARTED (should fail)
        success = self.state_machine.transition_record("12345", ApplicationState.APPLY_STARTED)
        self.assertFalse(success)
    
    def test_duplicate_detection_by_job_id(self):
        """Test duplicate detection by job ID."""
        # Create first record and mark as submitted
        self.state_machine.create_record(
            job_id="12345",
            job_url="https://www.naukri.com/jobs/12345",
            title="Test Job",
            company="Test Company",
        )
        # Transition through proper states
        self.state_machine.transition_record("12345", ApplicationState.FILTERED)
        self.state_machine.transition_record("12345", ApplicationState.OPENED)
        self.state_machine.transition_record("12345", ApplicationState.APPLY_STARTED)
        self.state_machine.transition_record("12345", ApplicationState.SCREENING)
        self.state_machine.transition_record("12345", ApplicationState.SUBMISSION_ATTEMPTED)
        self.state_machine.transition_record("12345", ApplicationState.SUBMITTED)
        
        # Check for duplicate
        is_duplicate, existing = self.state_machine.is_duplicate(
            job_id="12345",
            job_url="https://www.naukri.com/jobs/12345",
            company="Test Company",
            title="Test Job",
        )
        self.assertTrue(is_duplicate)
        self.assertIsNotNone(existing)
    
    def test_duplicate_detection_by_url(self):
        """Test duplicate detection by normalized URL."""
        # Create first record and mark as submitted
        self.state_machine.create_record(
            job_id="12345",
            job_url="https://www.naukri.com/jobs/12345?param=value",
            title="Test Job",
            company="Test Company",
        )
        # Transition through proper states
        self.state_machine.transition_record("12345", ApplicationState.FILTERED)
        self.state_machine.transition_record("12345", ApplicationState.OPENED)
        self.state_machine.transition_record("12345", ApplicationState.APPLY_STARTED)
        self.state_machine.transition_record("12345", ApplicationState.SCREENING)
        self.state_machine.transition_record("12345", ApplicationState.SUBMISSION_ATTEMPTED)
        self.state_machine.transition_record("12345", ApplicationState.SUBMITTED)
        
        # Check for duplicate with different query parameters
        is_duplicate, existing = self.state_machine.is_duplicate(
            job_id="67890",
            job_url="https://www.naukri.com/jobs/12345?other=param",
            company="Test Company",
            title="Test Job",
        )
        self.assertTrue(is_duplicate)
    
    def test_duplicate_detection_by_company_title(self):
        """Test duplicate detection by company + title."""
        # Create first record and mark as submitted
        self.state_machine.create_record(
            job_id="12345",
            job_url="https://www.naukri.com/jobs/12345",
            title="Test Job",
            company="Test Company",
        )
        # Transition through proper states
        self.state_machine.transition_record("12345", ApplicationState.FILTERED)
        self.state_machine.transition_record("12345", ApplicationState.OPENED)
        self.state_machine.transition_record("12345", ApplicationState.APPLY_STARTED)
        self.state_machine.transition_record("12345", ApplicationState.SCREENING)
        self.state_machine.transition_record("12345", ApplicationState.SUBMISSION_ATTEMPTED)
        self.state_machine.transition_record("12345", ApplicationState.SUBMITTED)
        
        # Check for duplicate with different job ID but same company/title
        is_duplicate, existing = self.state_machine.is_duplicate(
            job_id="67890",
            job_url="https://www.naukri.com/jobs/67890",
            company="Test Company",
            title="Test Job",
        )
        self.assertTrue(is_duplicate)
    
    def test_get_uncertain_applications(self):
        """Test retrieving uncertain applications."""
        # Create uncertain application
        self.state_machine.create_record(
            job_id="12345",
            job_url="https://www.naukri.com/jobs/12345",
            title="Test Job",
            company="Test Company",
        )
        # Transition through proper states to SUBMISSION_ATTEMPTED, then to UNCERTAIN
        self.state_machine.transition_record("12345", ApplicationState.FILTERED)
        self.state_machine.transition_record("12345", ApplicationState.OPENED)
        self.state_machine.transition_record("12345", ApplicationState.APPLY_STARTED)
        self.state_machine.transition_record("12345", ApplicationState.SCREENING)
        self.state_machine.transition_record("12345", ApplicationState.SUBMISSION_ATTEMPTED)
        self.state_machine.transition_record("12345", ApplicationState.UNCERTAIN)
        
        uncertain = self.state_machine.get_uncertain_applications()
        self.assertEqual(len(uncertain), 1)
        self.assertEqual(uncertain[0].job_id, "12345")
    
    def test_get_security_stopped_applications(self):
        """Test retrieving security-stopped applications."""
        # Create security-stopped application
        self.state_machine.create_record(
            job_id="12345",
            job_url="https://www.naukri.com/jobs/12345",
            title="Test Job",
            company="Test Company",
        )
        # Transition through proper states to APPLY_STARTED, then to SECURITY_STOP
        self.state_machine.transition_record("12345", ApplicationState.FILTERED)
        self.state_machine.transition_record("12345", ApplicationState.OPENED)
        self.state_machine.transition_record("12345", ApplicationState.APPLY_STARTED)
        self.state_machine.transition_record("12345", ApplicationState.SECURITY_STOP)
        
        stopped = self.state_machine.get_security_stopped_applications()
        self.assertEqual(len(stopped), 1)
        self.assertEqual(stopped[0].job_id, "12345")
    
    def test_state_persistence(self):
        """Test state persistence across instances."""
        # Create record and transition through proper states
        self.state_machine.create_record(
            job_id="12345",
            job_url="https://www.naukri.com/jobs/12345",
            title="Test Job",
            company="Test Company",
        )
        self.state_machine.transition_record("12345", ApplicationState.FILTERED)
        self.state_machine.transition_record("12345", ApplicationState.OPENED)
        self.state_machine.transition_record("12345", ApplicationState.APPLY_STARTED)
        self.state_machine.transition_record("12345", ApplicationState.SCREENING)
        self.state_machine.transition_record("12345", ApplicationState.SUBMISSION_ATTEMPTED)
        self.state_machine.transition_record("12345", ApplicationState.SUBMITTED)
        
        # Create new instance (should load from file)
        new_state_machine = ApplicationStateMachine(str(self.state_file))
        record = new_state_machine.get_record("12345")
        self.assertIsNotNone(record)
        self.assertEqual(record.state, ApplicationState.SUBMITTED)


class TestSafetyConfig(unittest.TestCase):
    """Test safety configuration."""
    
    def test_default_config(self):
        """Test default safety configuration."""
        config = SafetyConfig.load()
        self.assertTrue(config.stop_on_security_event)
        self.assertTrue(config.stop_on_captcha)
        self.assertTrue(config.stop_on_rate_limit)
        self.assertTrue(config.emergency_stop_enabled)
        self.assertEqual(config.max_applications_per_hour, 3)
        self.assertEqual(config.max_applications_per_day, 5)
        self.assertEqual(config.max_retries, 2)
        self.assertFalse(config.llm_data_sharing)
        self.assertFalse(config.save_debug_artifacts)
    
    def test_custom_config(self):
        """Test custom safety configuration from profile."""
        profile_data = {
            "max_applications_per_hour": 5,
            "max_applications_per_day": 10,
            "max_retries": 3,
            "stop_on_captcha": False,
        }
        config = SafetyConfig.load(profile_data)
        self.assertEqual(config.max_applications_per_hour, 5)
        self.assertEqual(config.max_applications_per_day, 10)
        self.assertEqual(config.max_retries, 3)
        self.assertFalse(config.stop_on_captcha)
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = SafetyConfig()
        config.max_applications_per_hour = -1
        errors = config.validate()
        self.assertTrue(len(errors) > 0)
        self.assertTrue(any("hour" in error.lower() for error in errors))
    
    def test_invalid_hour_greater_than_day(self):
        """Test that hourly limit cannot exceed daily limit."""
        config = SafetyConfig()
        config.max_applications_per_hour = 10
        config.max_applications_per_day = 5
        errors = config.validate()
        self.assertTrue(len(errors) > 0)


class TestRetryHandler(unittest.TestCase):
    """Test safe retry handler."""
    
    def setUp(self):
        self.handler = RetryHandler(max_retries=2)
    
    def test_transient_error_is_retryable(self):
        """Test that transient errors are retryable."""
        error = Exception("Timeout waiting for element")
        self.assertTrue(self.handler.is_transient_error(error))
    
    def test_security_error_not_retryable(self):
        """Test that security errors are not retryable."""
        error = Exception("CAPTCHA detected")
        self.assertFalse(self.handler.is_transient_error(error))
        self.assertTrue(self.handler.is_security_error(error))
    
    def test_security_error_never_retried(self):
        """Test that security errors are never retried."""
        call_count = 0
        
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise Exception("CAPTCHA detected")
        
        with self.assertRaises(Exception):
            self.handler.execute_with_retry(failing_function, "test operation")
        
        # Should only be called once (no retries for security errors)
        self.assertEqual(call_count, 1)
    
    def test_transient_error_retried(self):
        """Test that transient errors are retried."""
        call_count = 0
        
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Timeout waiting for element")
            return "success"
        
        result = self.handler.execute_with_retry(failing_function, "test operation")
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 2)  # Failed once, succeeded on retry
    
    def test_max_retries_respected(self):
        """Test that max retries is respected."""
        call_count = 0
        
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise Exception("Timeout waiting for element")
        
        with self.assertRaises(Exception):
            self.handler.execute_with_retry(failing_function, "test operation")
        
        # Should be called max_retries + 1 times (initial + retries)
        self.assertEqual(call_count, 3)


class TestApplicationLimiter(unittest.TestCase):
    """Test application limiter."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = Path(self.temp_dir) / "application_limits.json"
        self.limiter = ApplicationLimiter(
            max_per_run=5,
            max_per_hour=3,
            max_per_day=5,
            state_file=str(self.state_file),
        )
    
    def test_can_submit_initially(self):
        """Test that submissions are allowed initially."""
        self.assertTrue(self.limiter.can_submit())
    
    def test_record_application(self):
        """Test recording an application."""
        self.assertTrue(self.limiter.record_application())
        self.assertEqual(self.limiter.run_count, 1)
    
    def test_run_limit_enforced(self):
        """Test that run limit is enforced."""
        for _ in range(5):
            self.limiter.record_application()
        
        self.assertFalse(self.limiter.can_submit())
    
    def test_hourly_limit_enforced(self):
        """Test that hourly limit is enforced."""
        # Manually add hourly timestamps
        now = datetime.now()
        for _ in range(3):
            self.limiter.hourly_timestamps.append(now.isoformat())
        
        self.assertFalse(self.limiter.can_submit())
    
    def test_daily_limit_enforced(self):
        """Test that daily limit is enforced."""
        # Manually add daily timestamps
        now = datetime.now()
        for _ in range(5):
            self.limiter.daily_timestamps.append(now.isoformat())
        
        self.assertFalse(self.limiter.can_submit())
    
    def test_old_timestamps_cleaned(self):
        """Test that old timestamps are cleaned up."""
        # Add old timestamp
        old_time = datetime.now() - timedelta(hours=2)
        self.limiter.hourly_timestamps.append(old_time.isoformat())
        
        # Trigger cleanup
        self.limiter._cleanup_old_timestamps()
        
        # Old timestamp should be removed
        self.assertEqual(len(self.limiter.hourly_timestamps), 0)
    
    def test_reset_run_count(self):
        """Test resetting run count."""
        self.limiter.record_application()
        self.assertEqual(self.limiter.run_count, 1)
        
        self.limiter.reset_run_count()
        self.assertEqual(self.limiter.run_count, 0)
    
    def test_get_counts(self):
        """Test getting application counts."""
        self.limiter.record_application()
        counts = self.limiter.get_counts()
        self.assertEqual(counts["run_count"], 1)
        self.assertEqual(counts["remaining_run"], 4)


if __name__ == "__main__":
    unittest.main()
