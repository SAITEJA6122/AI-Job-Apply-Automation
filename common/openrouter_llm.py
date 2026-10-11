"""
Generates free-text screening answers using OpenRouter API.

Get a free key at https://openrouter.ai/keys
Set it as an environment variable before running:
    export OPENROUTER_API_KEY="your-key-here"
"""
import os
from pathlib import Path
import requests

MODEL = "meta-llama/llama-3.2-3b-instruct"  # Model on OpenRouter

_SYSTEM_INSTRUCTIONS = """\
You are drafting a short answer to a job-application screening question, in the
voice of the real applicant described below. Rules, no exceptions:

1. Only use facts given in the applicant profile and work history. Never invent
   an employer, tool, certification, number, or claim not present below.
2. If the question asks about something not covered by the profile, write
   exactly: [NEEDS_HUMAN_INPUT: <one line describing what's missing>]
   and nothing else.
3. Keep answers to 2-4 sentences. No generic filler adjectives ("passionate",
   "detail-oriented", "hard-working") unless the applicant's own words use them.
4. Write in first person, plainly, the way the applicant actually described
   themselves -- not marketing copy.
"""

def _load_dotenv_key():
    """Reads OPENROUTER_API_KEY out of a local .env file if the environment
    variable isn't already set. Looks in the project root (two levels up
    from this file: common/openrouter_llm.py -> project root)."""
    if os.environ.get("OPENROUTER_API_KEY"):
        return
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key.strip() == "OPENROUTER_API_KEY":
            os.environ["OPENROUTER_API_KEY"] = value.strip()
            return


def _get_api_key():
    """Get the OpenRouter API key from environment or .env file."""
    _load_dotenv_key()
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        return None
    return key


def draft_answer(question: str, profile_data: dict, job_context: str = "") -> str:
    """Returns a drafted answer, or a string starting with [NEEDS_HUMAN_INPUT: ...]
    if the profile doesn't actually cover what's being asked."""
    api_key = _get_api_key()
    if api_key is None:
        raise RuntimeError("OPENROUTER_API_KEY not set - no API key available")
    
    prompt = f"""{_SYSTEM_INSTRUCTIONS}

APPLICANT PROFILE:
{profile_data}

JOB CONTEXT (title/company/description, may be partial):
{job_context}

SCREENING QUESTION:
{question}

Draft the answer now."""
    
    try:
        print(f"[OpenRouter] Calling API with model: {MODEL}")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": _SYSTEM_INSTRUCTIONS},
                    {"role": "user", "content": prompt}
                ],
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        answer = result["choices"][0]["message"]["content"].strip()
        print(f"[OpenRouter] Answer received: {answer[:100]}...")
        return answer
    except requests.exceptions.RequestException as e:
        print(f"[OpenRouter] API error: {e}")
        print(f"[OpenRouter] Response status: {response.status_code if 'response' in locals() else 'N/A'}")
        print(f"[OpenRouter] Response body: {response.text if 'response' in locals() else 'N/A'}")
        raise RuntimeError(f"OpenRouter API error: {e}")
