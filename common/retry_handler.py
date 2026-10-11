"""
Safe Retry Handler

Implements safe retry logic with strict rules:
- Maximum 2 retries for transient technical failures
- NEVER retry security events
- NEVER retry CAPTCHA, verification, rate limits, auth failures
"""
import time
from typing import Callable, TypeVar, Optional

T = TypeVar('T')


class RetryHandler:
    """
    Safe retry handler with strict rules about what can be retried.
    
    Only transient technical failures can be retried.
    Security events are never retried (fail-closed behavior).
    """
    
    # Transient error keywords that allow retry
    TRANSIENT_ERROR_KEYWORDS = [
        "timeout",
        "timed out",
        "connection",
        "network",
        "temporary",
        "context was destroyed",
        "target closed",
    ]
    
    # Security error keywords that NEVER allow retry
    SECURITY_ERROR_KEYWORDS = [
        "captcha",
        "verify",
        "unusual activity",
        "suspicious activity",
        "account restriction",
        "blocked",
        "rate limit",
        "too many",
        "login",
        "session",
        "authentication",
        "forbidden",
        "401",
        "403",
        "429",
        "checkpoint",
        "otp",
        "2fa",
    ]
    
    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries
    
    def is_transient_error(self, error: Exception) -> bool:
        """
        Check if an error is a transient technical failure that can be retried.
        
        Returns True if the error is transient, False otherwise.
        """
        error_text = str(error).lower()
        
        # Check for security-related keywords first (fail-closed)
        for keyword in self.SECURITY_ERROR_KEYWORDS:
            if keyword in error_text:
                return False
        
        # Check for transient keywords
        for keyword in self.TRANSIENT_ERROR_KEYWORDS:
            if keyword in error_text:
                return True
        
        # Default: don't retry unknown errors
        return False
    
    def is_security_error(self, error: Exception) -> bool:
        """
        Check if an error is security-related and should never be retried.
        
        Returns True if the error is security-related, False otherwise.
        """
        error_text = str(error).lower()
        
        for keyword in self.SECURITY_ERROR_KEYWORDS:
            if keyword in error_text:
                return True
        
        return False
    
    def execute_with_retry(
        self,
        func: Callable[[], T],
        operation_name: str = "operation",
        delay_seconds: float = 1.0,
    ) -> T:
        """
        Execute a function with safe retry logic.
        
        Args:
            func: The function to execute
            operation_name: Name of the operation for logging
            delay_seconds: Delay between retries
        
        Returns:
            The result of the function
        
        Raises:
            The original exception if all retries are exhausted or if the error is not retryable
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func()
            except Exception as e:
                last_error = e
                
                # Check if this is a security error - never retry
                if self.is_security_error(e):
                    print(f"  ({operation_name} failed with security error: {e})")
                    print(f"  (Security errors are never retried - fail-closed behavior)")
                    raise
                
                # Check if this is a transient error - allow retry
                if self.is_transient_error(e):
                    if attempt < self.max_retries:
                        print(f"  ({operation_name} failed (attempt {attempt + 1}/{self.max_retries + 1}): {e})")
                        print(f"  (Retrying in {delay_seconds}s...)")
                        time.sleep(delay_seconds)
                        continue
                    else:
                        print(f"  ({operation_name} failed after {self.max_retries + 1} attempts: {e})")
                        raise
                else:
                    # Not a transient error - don't retry
                    print(f"  ({operation_name} failed with non-transient error: {e})")
                    print(f"  (Non-transient errors are not retried)")
                    raise
        
        # This should never be reached, but just in case
        if last_error:
            raise last_error
        raise RuntimeError("Retry handler failed without exception")


# Global retry handler instance
_retry_handler = None


def get_retry_handler(max_retries: int = 2) -> RetryHandler:
    """
    Get the global retry handler instance.
    """
    global _retry_handler
    if _retry_handler is None:
        _retry_handler = RetryHandler(max_retries)
    return _retry_handler
