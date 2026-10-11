"""
Unit tests for validation module.
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.validation import (
    sanitize_string,
    validate_email,
    validate_phone,
    validate_url,
    validate_skills,
    validate_number,
    validate_text_field,
    validate_profile_data,
    sanitize_login_credentials,
    ValidationError
)


class TestSanitizeString:
    """Test string sanitization."""

    def test_basic_string(self):
        """Test basic string sanitization."""
        result = sanitize_string("Hello World")
        assert result == "Hello World"

    def test_html_escaping(self):
        """Test HTML escaping."""
        result = sanitize_string("<script>alert('xss')</script>")
        assert "&lt;" in result
        assert "&gt;" in result
        assert "<script>" not in result

    def test_null_byte_removal(self):
        """Test null byte removal."""
        result = sanitize_string("Hello\x00World")
        assert "\x00" not in result

    def test_whitespace_trimming(self):
        """Test whitespace trimming."""
        result = sanitize_string("  Hello World  ")
        assert result == "Hello World"

    def test_max_length_enforcement(self):
        """Test max length enforcement."""
        with pytest.raises(ValidationError):
            sanitize_string("a" * 1001, max_length=1000)

    def test_non_string_input(self):
        """Test non-string input."""
        with pytest.raises(ValidationError):
            sanitize_string(123)


class TestValidateEmail:
    """Test email validation."""

    def test_valid_email(self):
        """Test valid email."""
        result = validate_email("test@example.com")
        assert result == "test@example.com"

    def test_email_normalization(self):
        """Test email normalization."""
        result = validate_email("Test@Example.COM")
        assert result == "test@example.com"

    def test_invalid_email(self):
        """Test invalid email."""
        with pytest.raises(ValidationError):
            validate_email("invalid-email")

    def test_empty_email(self):
        """Test empty email."""
        with pytest.raises(ValidationError):
            validate_email("")


class TestValidatePhone:
    """Test phone number validation."""

    def test_valid_phone(self):
        """Test valid phone number."""
        result = validate_phone("+1 (555) 123-4567")
        assert result == "15551234567"

    def test_short_phone(self):
        """Test too short phone number."""
        with pytest.raises(ValidationError):
            validate_phone("123")

    def test_long_phone(self):
        """Test too long phone number."""
        with pytest.raises(ValidationError):
            validate_phone("1" * 16)


class TestValidateUrl:
    """Test URL validation."""

    def test_valid_http_url(self):
        """Test valid HTTP URL."""
        result = validate_url("http://example.com")
        assert result == "http://example.com"

    def test_valid_https_url(self):
        """Test valid HTTPS URL."""
        result = validate_url("https://example.com")
        assert result == "https://example.com"

    def test_invalid_url(self):
        """Test invalid URL."""
        with pytest.raises(ValidationError):
            validate_url("not-a-url")

    def test_non_string_url(self):
        """Test non-string URL."""
        with pytest.raises(ValidationError):
            validate_url(123)


class TestValidateSkills:
    """Test skills validation."""

    def test_valid_skills(self):
        """Test valid skills list."""
        result = validate_skills(["Python", "JavaScript", "React"])
        assert len(result) == 3
        assert "Python" in result

    def test_skill_special_chars(self):
        """Test special character removal."""
        result = validate_skills(["Python!", "Java@#"])
        assert "Python" in result
        assert "Java" in result

    def test_empty_skills(self):
        """Test empty skills."""
        result = validate_skills([])
        assert result == []

    def test_long_skill(self):
        """Test skill too long."""
        with pytest.raises(ValidationError):
            validate_skills(["a" * 51])

    def test_non_list_skills(self):
        """Test non-list input."""
        with pytest.raises(ValidationError):
            validate_skills("not a list")


class TestValidateNumber:
    """Test number validation."""

    def test_valid_number(self):
        """Test valid number."""
        result = validate_number(42)
        assert result == 42.0

    def test_string_number(self):
        """Test string number."""
        result = validate_number("42")
        assert result == 42.0

    def test_min_value(self):
        """Test minimum value."""
        result = validate_number(10, min_val=5)
        assert result == 10.0

    def test_below_min_value(self):
        """Test below minimum value."""
        with pytest.raises(ValidationError):
            validate_number(3, min_val=5)

    def test_max_value(self):
        """Test maximum value."""
        result = validate_number(10, max_val=20)
        assert result == 10.0

    def test_above_max_value(self):
        """Test above maximum value."""
        with pytest.raises(ValidationError):
            validate_number(30, max_val=20)

    def test_invalid_number(self):
        """Test invalid number."""
        with pytest.raises(ValidationError):
            validate_number("not a number")


class TestValidateProfileData:
    """Test profile data validation."""

    def test_valid_profile(self):
        """Test valid profile data."""
        profile = {
            "email": "test@example.com",
            "phone": "1234567890",
            "full_name": "John Doe",
            "skills": ["Python", "JavaScript"]
        }
        result = validate_profile_data(profile)
        assert result["email"] == "test@example.com"
        assert result["phone"] == "1234567890"

    def test_invalid_email_in_profile(self):
        """Test invalid email in profile."""
        profile = {"email": "invalid-email"}
        with pytest.raises(ValidationError):
            validate_profile_data(profile)

    def test_numeric_fields(self):
        """Test numeric field validation."""
        profile = {
            "total_experience_years": 5,
            "current_ctc_lpa": 10.5
        }
        result = validate_profile_data(profile)
        assert result["total_experience_years"] == 5.0
        assert result["current_ctc_lpa"] == 10.5


class TestSanitizeLoginCredentials:
    """Test login credential sanitization."""

    def test_valid_credentials(self):
        """Test valid credentials."""
        credentials = {
            "email": "test@example.com",
            "password": "password123"
        }
        result = sanitize_login_credentials(credentials)
        assert result["email"] == "test@example.com"
        assert result["password"] == "password123"

    def test_missing_email(self):
        """Test missing email."""
        credentials = {"password": "password123"}
        with pytest.raises(ValidationError):
            sanitize_login_credentials(credentials)

    def test_missing_password(self):
        """Test missing password."""
        credentials = {"email": "test@example.com"}
        with pytest.raises(ValidationError):
            sanitize_login_credentials(credentials)

    def test_short_password(self):
        """Test short password."""
        credentials = {
            "email": "test@example.com",
            "password": "12345"
        }
        with pytest.raises(ValidationError):
            sanitize_login_credentials(credentials)

    def test_long_password(self):
        """Test long password."""
        credentials = {
            "email": "test@example.com",
            "password": "a" * 129
        }
        with pytest.raises(ValidationError):
            sanitize_login_credentials(credentials)
