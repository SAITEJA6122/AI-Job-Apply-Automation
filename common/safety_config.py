"""
Safety Configuration

Centralizes all safety and security configuration settings.
Works alongside profile.yaml to provide safety-specific configuration.
"""
import yaml
from pathlib import Path
from typing import Optional


class SafetyConfig:
    """
    Safety configuration settings.
    
    These settings control security, limits, and fail-closed behavior.
    They are loaded from profile.yaml if present, otherwise use safe defaults.
    """
    
    # Security event handling
    stop_on_security_event: bool = True
    stop_on_captcha: bool = True
    stop_on_rate_limit: bool = True
    stop_on_authentication_error: bool = True
    emergency_stop_enabled: bool = True
    
    # Application limits
    max_applications_per_run: int = 5
    max_applications_per_hour: int = 15
    max_applications_per_day: int = 50
    
    # Retry settings
    max_retries: int = 2  # Maximum retries for transient technical failures
    
    # Privacy settings
    llm_data_sharing: bool = False
    save_debug_artifacts: bool = False
    
    # Session security
    validate_session_on_startup: bool = True
    
    @classmethod
    def load(cls, profile_data: Optional[dict] = None) -> "SafetyConfig":
        """
        Load safety configuration from profile data.
        
        If profile_data is provided, use safety settings from it.
        Otherwise, use safe defaults.
        """
        config = cls()
        
        if profile_data:
            # Load safety settings from profile if present
            config.stop_on_security_event = profile_data.get("stop_on_security_event", config.stop_on_security_event)
            config.stop_on_captcha = profile_data.get("stop_on_captcha", config.stop_on_captcha)
            config.stop_on_rate_limit = profile_data.get("stop_on_rate_limit", config.stop_on_rate_limit)
            config.stop_on_authentication_error = profile_data.get("stop_on_authentication_error", config.stop_on_authentication_error)
            config.emergency_stop_enabled = profile_data.get("emergency_stop_enabled", config.emergency_stop_enabled)
            
            config.max_applications_per_hour = profile_data.get("max_applications_per_hour", config.max_applications_per_hour)
            config.max_applications_per_day = profile_data.get("max_applications_per_day", config.max_applications_per_day)
            
            config.max_retries = profile_data.get("max_retries", config.max_retries)
            
            config.llm_data_sharing = profile_data.get("llm_data_sharing", config.llm_data_sharing)
            config.save_debug_artifacts = profile_data.get("save_debug_artifacts", config.save_debug_artifacts)
            
            config.validate_session_on_startup = profile_data.get("validate_session_on_startup", config.validate_session_on_startup)
            
            # Note: max_applications_per_run is already in profile.yaml as stop_after_n_applications
            # We don't override it here to preserve existing behavior
        
        return config
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "stop_on_security_event": self.stop_on_security_event,
            "stop_on_captcha": self.stop_on_captcha,
            "stop_on_rate_limit": self.stop_on_rate_limit,
            "stop_on_authentication_error": self.stop_on_authentication_error,
            "emergency_stop_enabled": self.emergency_stop_enabled,
            "max_applications_per_run": self.max_applications_per_run,
            "max_applications_per_hour": self.max_applications_per_hour,
            "max_applications_per_day": self.max_applications_per_day,
            "max_retries": self.max_retries,
            "llm_data_sharing": self.llm_data_sharing,
            "save_debug_artifacts": self.save_debug_artifacts,
            "validate_session_on_startup": self.validate_session_on_startup,
        }
    
    def validate(self) -> list[str]:
        """
        Validate configuration settings.
        
        Returns a list of validation errors (empty if valid).
        """
        errors = []
        
        if self.max_applications_per_hour <= 0:
            errors.append("max_applications_per_hour must be positive")
        
        if self.max_applications_per_day <= 0:
            errors.append("max_applications_per_day must be positive")
        
        if self.max_applications_per_hour > self.max_applications_per_day:
            errors.append("max_applications_per_hour cannot exceed max_applications_per_day")
        
        if self.max_retries < 0:
            errors.append("max_retries cannot be negative")
        
        return errors
