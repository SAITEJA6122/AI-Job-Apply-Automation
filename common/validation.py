"""
Input validation and sanitization utilities.

This module provides functions to validate and sanitize user inputs
to prevent injection attacks and ensure data integrity.
"""
import re
import html
from typing import Optional, List, Any
from email_validator import validate_email as validate_email_address, EmailNotValidError


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def sanitize_string(input_string: str, max_length: int = 1000) -> str:
    """
    Sanitize a string input.

    Args:
        input_string: The string to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string

    Raises:
        ValidationError: If input is invalid
    """
    if not isinstance(input_string, str):
        raise ValidationError("Input must be a string")

    # Remove null bytes
    input_string = input_string.replace('\x00', '')

    # Trim whitespace
    input_string = input_string.strip()

    # Check length
    if len(input_string) > max_length:
        raise ValidationError(f"Input exceeds maximum length of {max_length}")

    # HTML escape to prevent XSS
    input_string = html.escape(input_string)

    return input_string


def validate_email(email: str) -> str:
    """
    Validate and sanitize email address.

    Args:
        email: Email address to validate

    Returns:
        Sanitized email address

    Raises:
        ValidationError: If email is invalid
    """
    try:
        # Validate email format
        validated = validate_email_address(email)
        return validated.email.lower().strip()
    except EmailNotValidError as e:
        raise ValidationError(f"Invalid email address: {str(e)}")


def validate_phone(phone: str) -> str:
    """
    Validate and sanitize phone number.

    Args:
        phone: Phone number to validate

    Returns:
        Sanitized phone number

    Raises:
        ValidationError: If phone is invalid
    """
    # Remove all non-digit characters
    digits = re.sub(r'[^\d]', '', phone)

    # Check length (assuming 10-15 digits for international numbers)
    if not 10 <= len(digits) <= 15:
        raise ValidationError("Phone number must be between 10-15 digits")

    return digits


def validate_url(url: str) -> str:
    """
    Validate and sanitize URL.

    Args:
        url: URL to validate

    Returns:
        Sanitized URL

    Raises:
        ValidationError: If URL is invalid
    """
    if not isinstance(url, str):
        raise ValidationError("URL must be a string")

    url = url.strip()

    # Basic URL pattern
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if not url_pattern.match(url):
        raise ValidationError("Invalid URL format")

    return url


def validate_skills(skills: List[str]) -> List[str]:
    """
    Validate and sanitize skills list.

    Args:
        skills: List of skills to validate

    Returns:
        Sanitized list of skills

    Raises:
        ValidationError: If skills are invalid
    """
    if not isinstance(skills, list):
        raise ValidationError("Skills must be a list")

    sanitized = []
    for skill in skills:
        if not isinstance(skill, str):
            raise ValidationError("Each skill must be a string")

        skill = skill.strip()
        if not skill:
            continue

        # Remove special characters except hyphens and spaces
        skill = re.sub(r'[^\w\s-]', '', skill)
        skill = ' '.join(skill.split())  # Normalize whitespace

        if len(skill) > 50:
            raise ValidationError(f"Skill '{skill}' exceeds maximum length of 50")

        sanitized.append(skill)

    return sanitized


def validate_number(value: Any, min_val: Optional[float] = None, max_val: Optional[float] = None) -> float:
    """
    Validate and sanitize numeric input.

    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Validated numeric value

    Raises:
        ValidationError: If value is invalid
    """
    try:
        num = float(value)
    except (ValueError, TypeError):
        raise ValidationError("Value must be a number")

    if min_val is not None and num < min_val:
        raise ValidationError(f"Value must be at least {min_val}")

    if max_val is not None and num > max_val:
        raise ValidationError(f"Value must be at most {max_val}")

    return num


def validate_text_field(field_name: str, value: Any, required: bool = True,
                       min_length: int = 0, max_length: int = 500) -> str:
    """
    Validate a generic text field.

    Args:
        field_name: Name of the field (for error messages)
        value: Value to validate
        required: Whether the field is required
        min_length: Minimum length
        max_length: Maximum length

    Returns:
        Validated string

    Raises:
        ValidationError: If value is invalid
    """
    if value is None or value == '':
        if required:
            raise ValidationError(f"{field_name} is required")
        return ''

    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")

    value = value.strip()

    if len(value) < min_length:
        raise ValidationError(f"{field_name} must be at least {min_length} characters")

    if len(value) > max_length:
        raise ValidationError(f"{field_name} must not exceed {max_length} characters")

    return value


def validate_profile_data(profile_data: dict) -> dict:
    """
    Validate complete profile data.

    Args:
        profile_data: Dictionary containing profile data

    Returns:
        Validated and sanitized profile data

    Raises:
        ValidationError: If profile data is invalid
    """
    validated = {}

    # Validate required fields
    if 'email' in profile_data:
        validated['email'] = validate_email(profile_data['email'])

    if 'phone' in profile_data:
        validated['phone'] = validate_phone(profile_data['phone'])

    if 'full_name' in profile_data:
        validated['full_name'] = validate_text_field(
            'Full Name', profile_data['full_name'],
            min_length=2, max_length=100
        )

    if 'current_city' in profile_data:
        validated['current_city'] = validate_text_field(
            'Current City', profile_data['current_city'],
            required=False, max_length=100
        )

    if 'linkedin' in profile_data and profile_data['linkedin']:
        validated['linkedin'] = validate_url(profile_data['linkedin'])

    if 'github' in profile_data and profile_data['github']:
        validated['github'] = validate_url(profile_data['github'])

    if 'skills' in profile_data:
        validated['skills'] = validate_skills(profile_data['skills'])

    # Validate numeric fields
    if 'total_experience_years' in profile_data:
        validated['total_experience_years'] = validate_number(
            profile_data['total_experience_years'],
            min_val=0, max_val=50
        )

    if 'notice_period_days' in profile_data:
        validated['notice_period_days'] = validate_number(
            profile_data['notice_period_days'],
            min_val=0, max_val=365
        )

    if 'current_ctc_lpa' in profile_data:
        validated['current_ctc_lpa'] = validate_number(
            profile_data['current_ctc_lpa'],
            min_val=0, max_val=100
        )

    if 'expected_ctc_lpa' in profile_data:
        validated['expected_ctc_lpa'] = validate_number(
            profile_data['expected_ctc_lpa'],
            min_val=0, max_val=100
        )

    # Copy over other fields that don't need validation
    for key, value in profile_data.items():
        if key not in validated:
            validated[key] = value

    return validated


def sanitize_login_credentials(credentials: dict) -> dict:
    """
    Validate and sanitize login credentials.

    Args:
        credentials: Dictionary with email and password

    Returns:
        Validated credentials

    Raises:
        ValidationError: If credentials are invalid
    """
    if not isinstance(credentials, dict):
        raise ValidationError("Credentials must be a dictionary")

    if 'email' not in credentials or not credentials['email']:
        raise ValidationError("Email is required")

    if 'password' not in credentials or not credentials['password']:
        raise ValidationError("Password is required")

    # Validate email
    validated_email = validate_email(credentials['email'])

    # Password validation (basic)
    password = credentials['password']
    if len(password) < 6:
        raise ValidationError("Password must be at least 6 characters")

    if len(password) > 128:
        raise ValidationError("Password must not exceed 128 characters")

    return {
        'email': validated_email,
        'password': password  # Don't sanitize password - we need the actual value
    }
