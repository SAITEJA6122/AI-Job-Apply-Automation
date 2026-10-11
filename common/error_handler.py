"""
Custom error handling and error messages.

This module provides custom error classes and error handling utilities
for better error messages and error recovery.
"""
from typing import Optional, Dict, Any
from enum import Enum


class ErrorCode(Enum):
    """Error codes for different types of errors."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    SESSION_ERROR = "SESSION_ERROR"
    FILE_ERROR = "FILE_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    AUTOMATION_ERROR = "AUTOMATION_ERROR"
    PROFILE_ERROR = "PROFILE_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class AppError(Exception):
    """Base exception class for application errors."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None
    ):
        """
        Initialize AppError.

        Args:
            message: Error message
            error_code: Error code from ErrorCode enum
            details: Additional error details
            suggestion: Suggested fix or action
        """
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.suggestion = suggestion
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses."""
        return {
            'error': self.message,
            'error_code': self.error_code.value,
            'details': self.details,
            'suggestion': self.suggestion
        }


class ValidationError(AppError):
    """Validation error for invalid input."""

    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        details = {'field': field} if field else {}
        suggestion = "Please check your input and try again."
        super().__init__(
            message,
            error_code=ErrorCode.VALIDATION_ERROR,
            details=details,
            suggestion=suggestion,
            **kwargs
        )


class AuthenticationError(AppError):
    """Authentication error for login/session issues."""

    def __init__(self, message: str, **kwargs):
        suggestion = "Please check your credentials and try again."
        super().__init__(
            message,
            error_code=ErrorCode.AUTHENTICATION_ERROR,
            suggestion=suggestion,
            **kwargs
        )


class SessionError(AppError):
    """Session error for session management issues."""

    def __init__(self, message: str, **kwargs):
        suggestion = "Please try logging in again."
        super().__init__(
            message,
            error_code=ErrorCode.SESSION_ERROR,
            suggestion=suggestion,
            **kwargs
        )


class FileError(AppError):
    """File error for file operations."""

    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        details = {'file_path': file_path} if file_path else {}
        suggestion = "Please check the file and try again."
        super().__init__(
            message,
            error_code=ErrorCode.FILE_ERROR,
            details=details,
            suggestion=suggestion,
            **kwargs
        )


class DatabaseError(AppError):
    """Database error for database operations."""

    def __init__(self, message: str, **kwargs):
        suggestion = "Please try again. If the problem persists, contact support."
        super().__init__(
            message,
            error_code=ErrorCode.DATABASE_ERROR,
            suggestion=suggestion,
            **kwargs
        )


class NetworkError(AppError):
    """Network error for connectivity issues."""

    def __init__(self, message: str, **kwargs):
        suggestion = "Please check your internet connection and try again."
        super().__init__(
            message,
            error_code=ErrorCode.NETWORK_ERROR,
            suggestion=suggestion,
            **kwargs
        )


class AutomationError(AppError):
    """Automation error for job application automation."""

    def __init__(self, message: str, step: Optional[str] = None, **kwargs):
        details = {'step': step} if step else {}
        suggestion = "Please check the automation logs and try again."
        super().__init__(
            message,
            error_code=ErrorCode.AUTOMATION_ERROR,
            details=details,
            suggestion=suggestion,
            **kwargs
        )


class ProfileError(AppError):
    """Profile error for profile management."""

    def __init__(self, message: str, **kwargs):
        suggestion = "Please check your profile configuration."
        super().__init__(
            message,
            error_code=ErrorCode.PROFILE_ERROR,
            suggestion=suggestion,
            **kwargs
        )


def handle_app_error(error: Exception) -> Dict[str, Any]:
    """
    Convert an exception to an error response dictionary.

    Args:
        error: Exception to handle

    Returns:
        Dictionary with error information
    """
    if isinstance(error, AppError):
        return error.to_dict()
    else:
        # Handle unknown errors
        return {
            'error': str(error),
            'error_code': ErrorCode.UNKNOWN_ERROR.value,
            'details': {},
            'suggestion': "An unexpected error occurred. Please try again."
        }


def get_user_friendly_message(error: Exception) -> str:
    """
    Get a user-friendly error message.

    Args:
        error: Exception to convert

    Returns:
        User-friendly error message
    """
    if isinstance(error, AppError):
        return error.message
    else:
        # Generic error message for unknown errors
        return "An unexpected error occurred. Please try again later."
