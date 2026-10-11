"""
Tries OpenRouter first for screening-answer drafting; if it's out of free-tier
quota (rate-limited or daily-exhausted), automatically falls back to Groq's
free tier, then Gemini instead of stopping the whole run.

If no API keys are configured, falls back to human input.

Optionally configure OPENROUTER_API_KEY, GROQ_API_KEY, or GEMINI_API_KEY in your .env file.
Having multiple means you effectively get multiple independent free quotas.

PRIVACY ENHANCEMENTS:
- Never sends passwords, cookies, or authentication tokens
- Filters sensitive profile data before sending to LLM
- Sends only minimal information required for the specific question
- Never allows AI to invent personal information
"""
from . import openrouter_llm
from . import groq_llm
from . import gemini

_QUOTA_ERROR_HINTS = ("429", "quota", "rate limit", "resource_exhausted", "exhausted")

# Sensitive fields that should NEVER be sent to LLM
SENSITIVE_PROFILE_FIELDS = {
    "password",
    "api_key",
    "secret",
    "token",
    "cookie",
    "authorization",
    "aadhar",
    "aadhaar",
    "pan",
    "passport",
    "bank_account",
    "ifsc",
    "father_name",
    "mother_name",
    "blood_group",
    "emergency_contact",
    "voter_id",
    "driving_licence",
    "driving_license",
}


def _looks_like_quota_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(hint in text for hint in _QUOTA_ERROR_HINTS)


def _sanitize_profile_data(profile_data: dict) -> dict:
    """
    Remove sensitive fields from profile data before sending to LLM.
    
    Returns a sanitized copy of profile data with sensitive fields removed.
    """
    sanitized = {}
    for key, value in profile_data.items():
        # Skip sensitive fields
        if any(sensitive in key.lower() for sensitive in SENSITIVE_PROFILE_FIELDS):
            continue
        
        # Skip session-related fields
        if "session" in key.lower() or "cookie" in key.lower():
            continue
        
        # Keep safe fields
        sanitized[key] = value
    
    return sanitized


def _sanitize_job_context(job_context: str) -> str:
    """
    Sanitize job context to remove any sensitive information.
    
    Currently a placeholder - job context is typically just title/company,
    which is safe to send.
    """
    # Remove any potential URLs or email addresses
    import re
    sanitized = re.sub(r'https?://\S+', '', job_context)
    sanitized = re.sub(r'\S+@\S+\.\S+', '', sanitized)
    return sanitized.strip()


def draft_answer(question: str, profile_data: dict, job_context: str = "") -> str:
    """
    Draft an answer using LLM with privacy protections.

    Args:
        question: The screening question
        profile_data: Applicant profile data (will be sanitized)
        job_context: Job title/company context (will be sanitized)

    Returns:
        Drafted answer or [NEEDS_HUMAN_INPUT: ...] if unable to answer
    """
    # Sanitize data before sending to LLM
    sanitized_profile = _sanitize_profile_data(profile_data)
    sanitized_job_context = _sanitize_job_context(job_context)

    # Try OpenRouter first
    try:
        return openrouter_llm.draft_answer(question, sanitized_profile, sanitized_job_context)
    except Exception as e:
        if not _looks_like_quota_error(e) and "no API key available" not in str(e).lower():
            raise
        print(f"  (OpenRouter unavailable — {e}. Falling back to Groq...)")

    # Try Groq second
    try:
        return groq_llm.draft_answer(question, sanitized_profile, sanitized_job_context)
    except Exception as e:
        if not _looks_like_quota_error(e) and "no API key available" not in str(e).lower():
            raise
        print(f"  (Groq unavailable — {e}. Falling back to Gemini...)")

    # Try Gemini third
    try:
        return gemini.draft_answer(question, sanitized_profile, sanitized_job_context)
    except Exception as e:
        if "no API key available" in str(e).lower():
            print(f"  (No API keys available - will ask for human input)")
            return "[NEEDS_HUMAN_INPUT: No API keys configured]"
        raise
