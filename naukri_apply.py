"""
Naukri auto-apply. Requires session_naukri.json from login_capture.py.

Usage:
    python naukri_apply.py

Stops the ENTIRE run immediately and reports if it hits a CAPTCHA, a login
prompt, or a rate-limit warning. Never attempts to solve any of those --
that's the point. Everything else (a bad selector, a question it can't
answer, a stray page error) is handled per-listing: that one listing is
skipped and logged, and the run continues.

ENHANCED WITH SECURITY CONTROLLER:
- Centralized security detection and fail-closed behavior
- Application state tracking and crash recovery
- Duplicate application protection
- Application limit enforcement (per run, per hour, per day)
- Emergency stop (Ctrl+C and STOP_AUTOMATION file)
- Session security validation
- Security event logging
"""
import csv
import time
import random
import signal
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from common.notifications import get_notification_service

from common.profile import Profile
from common import llm
from common import learned_answers
from common.human_input import ask_user
from common.security_controller import (
    SecurityController,
    SecurityEventType,
    get_security_controller,
)
from common.application_state import (
    ApplicationStateMachine,
    ApplicationState,
    get_application_state_machine,
)
from common.safety_config import SafetyConfig
from common.retry_handler import get_retry_handler
from common.application_limiter import get_application_limiter
from common.human_behavior import (
    human_typing,
    random_mouse_movement,
    natural_scroll,
    random_pause,
    human_click,
    reading_simulation,
    random_application_delay,
    enhanced_page_navigation,
    setup_human_like_context,
)

SESSION_FILE = "session_naukri.json"
LOG_FILE = "applications_log.csv"
STATS_FILE = "application_stats.json"

# Legacy STOP_PHRASES kept for backward compatibility
# New code uses SecurityController instead
STOP_PHRASES = [
    "too many requests", "unusual activity", "verify you are human",
    "captcha", "temporarily blocked", "please try again later and reduce",
    "there was an error while processing your request",
]

# Global emergency stop flag
_emergency_stop_requested = False


def handle_emergency_stop(signum=None, frame=None):
    """Handle emergency stop (Ctrl+C or STOP_AUTOMATION file)."""
    global _emergency_stop_requested
    _emergency_stop_requested = True
    print("\n" + "="*60)
    print("EMERGENCY STOP ACTIVATED")
    print("="*60)
    print("Saving state and closing safely...")
    print("="*60)


# Register signal handler for Ctrl+C
try:
    signal.signal(signal.SIGINT, handle_emergency_stop)
    signal.signal(signal.SIGTERM, handle_emergency_stop)
except Exception:
    # Signal handling may not work on all platforms
    pass

# Questions matching any of these should NEVER be answered by the LLM --
# these are exact personal facts an LLM could easily hallucinate wrong.
# Always routed straight to you (and then remembered for next time).
SENSITIVE_FIELD_HINTS = [
    "date of birth", "dob", "pan number", "pan card", "aadhar", "aadhaar",
    "passport", "bank account", "ifsc", "father's name", "father name",
    "mother's name", "mother name", "marital status", "blood group",
    "emergency contact", "voter id", "driving licence", "driving license",
]


# Specific phrases per answer-library key, checked as whole phrases (not
# single split words) so "current ctc" and "current city" can never collide
# just because they both start with "current". This is what the old
# key.split("_")[0] logic got wrong -- it reduced both to "current" and
# whichever key came first in the dict won, regardless of what was asked.
TRIGGER_PHRASES = {
    "years_experience": ["years of experience", "total experience", "how many years", "work experience"],
    "notice_period": ["notice period"],
    "current_ctc": ["current ctc", "current salary", "current compensation", "present ctc", "present salary"],
    "expected_ctc": ["expected ctc", "expected salary", "expected compensation"],
    "current_city": ["current city", "current location", "which city", "current place"],
    "relocate": ["relocate", "relocation", "willing to move"],
    "night_shift": ["night shift"],
    "weekend_work": ["weekend"],
}


def log_row(row: list):
    new_file = not Path(LOG_FILE).exists()
    with open(LOG_FILE, "a", newline="") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["timestamp", "source", "title", "company", "status", "reason", "error_category"])
        # Ensure row has at least 7 elements (pad with empty strings if needed)
        while len(row) < 7:
            row.append("")
        w.writerow(row[:7])  # Only write first 7 columns
        f.flush()  # Force write to disk immediately


def random_delay(min_seconds: float, max_seconds: float, action_name: str = "action"):
    """Adds a random delay to make behavior more human-like and reduce detection risk."""
    # Use enhanced human-like delay
    delay = random.uniform(min_seconds, max_seconds)
    print(f"  (waiting {delay:.1f}s before {action_name})")
    time.sleep(delay)
    # Add occasional small random pause
    if random.random() < 0.1:  # 10% chance
        extra_delay = random.uniform(0.5, 2.0)
        print(f"  (additional {extra_delay:.1f}s pause)")
        time.sleep(extra_delay)


def categorize_error(error_msg: str) -> str:
    """Categorizes errors for better analytics and debugging."""
    error_lower = error_msg.lower()
    
    if "timeout" in error_lower or "timed out" in error_lower:
        return "timeout"
    elif "network" in error_lower or "connection" in error_lower:
        return "network"
    elif "selector" in error_lower or "element" in error_lower:
        return "ui_element"
    elif "captcha" in error_lower or "verify" in error_lower:
        return "security"
    elif "login" in error_lower or "session" in error_lower:
        return "authentication"
    elif "rate limit" in error_lower or "too many" in error_lower:
        return "rate_limit"
    elif "profile" in error_lower or "answer" in error_lower:
        return "profile_data"
    elif "duplicate" in error_lower:
        return "duplicate"
    elif "limit" in error_lower:
        return "limit"
    elif "api key" in error_lower or "gemini" in error_lower or "openrouter" in error_lower:
        return "llm_api"
    elif "click" in error_lower:
        return "ui_element"
    else:
        return "unknown"


def passes_filters(card: dict, profile: Profile, role: str) -> tuple[bool, str]:
    title = (card.get("title") or "").lower()
    company = (card.get("company") or "").lower()
    location = (card.get("location") or "").lower()

    # Enhanced role matching with family groups
    required_keywords = profile.data.get("role_required_keywords", {}).get(role)
    if not required_keywords:
        print(f"  [DEBUG] No keywords found for role '{role}', using fallback")
        generic = {"engineer", "developer", "administrator", "analyst", "senior", "junior", "lead"}
        required_keywords = [w for w in role.lower().split() if w not in generic]
    else:
        print(f"  [DEBUG] Found {len(required_keywords)} keywords for role '{role}'")
    
    # Get role family groups for cross-role matching
    role_family_groups = profile.data.get("role_family_groups", {})
    # Find which family this role belongs to
    role_family_name = None
    family_roles = []
    for family_name, roles in role_family_groups.items():
        if role in roles:
            role_family_name = family_name
            family_roles = roles
            break
    
    # Check if title matches current role keywords OR any role in the same family
    matches_current_role = required_keywords and any(kw.lower() in title for kw in required_keywords)
    matches_family_role = False

    print(f"  [DEBUG] Checking title '{title}' against role '{role}'")
    print(f"  [DEBUG] Matches current role: {matches_current_role}")

    if role_family_name and not matches_current_role:
        # Try keywords from other roles in the same family
        print(f"  [DEBUG] Trying family roles in {role_family_name}")
        for family_role in family_roles:
            if family_role == role:
                continue
            family_keywords = profile.data.get("role_required_keywords", {}).get(family_role)
            if family_keywords and any(kw.lower() in title for kw in family_keywords):
                matches_family_role = True
                required_keywords = family_keywords  # Use the matching family's keywords
                print(f"  [DEBUG] Matched family role '{family_role}'")
                break

    if not matches_current_role and not matches_family_role:
        print(f"  [DEBUG] FAILED: Title doesn't match role keywords")
        return False, f"title doesn't match role keywords ({role})"

    for excl in profile.company_exclude:
        if excl.lower() in company:
            return False, f"company excluded ({excl})"

    if profile.company_include_only:
        if not any(inc.lower() in company for inc in profile.company_include_only):
            return False, "not in include-only list"

    exp_text = card.get("exp") or ""
    digits = [int(s) for s in exp_text.replace("Yrs", "").replace("yrs", "")
              .replace("-", " ").split() if s.isdigit()]
    if len(digits) >= 2:
        lo, hi = digits[0], digits[-1]
        if hi < profile.seniority_floor_years or lo > profile.seniority_ceiling_years:
            return False, f"experience range mismatch ({exp_text})"

    # Enhanced filtering: location preferences
    preferred_locations = profile.data.get("preferred_locations", [])
    if preferred_locations and location:
        if not any(loc.lower() in location for loc in preferred_locations):
            return False, f"location not preferred ({location})"

    # Enhanced filtering: exclude keywords in title
    exclude_keywords = profile.data.get("title_exclude_keywords", [])
    if exclude_keywords:
        if any(kw.lower() in title for kw in exclude_keywords):
            return False, f"title contains excluded keyword"

    return True, ""


def safe_evaluate(page, script, arg=None, default=None):
    """Runs page.evaluate but never lets a destroyed-context or stray JS error
    crash the whole run -- returns `default` instead. Naukri's own chat widget
    and SPA navigation can tear down the page mid-script, which raises
    Playwright's 'Execution context was destroyed' error; that's expected
    occasionally, not something to crash over."""
    try:
        return page.evaluate(script, arg) if arg is not None else page.evaluate(script)
    except Exception as e:
        print(f"  (page.evaluate failed, continuing anyway: {e})")
        return default


def enumerate_cards(page):
    """Reads real job cards off the search results page. Card wrapper is
    div.srp-jobtuple-wrapper with a data-job-id attribute -- that attribute
    is the reliable marker; filter/promo widgets on the same page don't
    have it."""
    return safe_evaluate(page, """
        () => Array.from(document.querySelectorAll('.srp-jobtuple-wrapper[data-job-id]'))
          .map((c, i) => ({
            i,
            jobId: c.getAttribute('data-job-id'),
            title: c.querySelector('a.title')?.innerText.trim(),
            href: c.querySelector('a.title')?.href,
            company: c.querySelector('a.comp-name, .comp-dtls-wrap a')?.innerText.trim(),
            exp: c.querySelector('.expwdth')?.innerText,
            location: c.querySelector('.locWdth')?.innerText,
          }))
          .filter(c => c.title && c.href)
    """, default=[]) or []


def check_apply_button(page) -> str:
    """Returns 'external', 'native', or 'none' based on the detail page's apply button."""
    # Check for external apply (company website redirect)
    if page.query_selector('#company-site-button'):
        return "external"
    # Check for redirect message
    page_text = page.inner_text("body").lower()
    if "redirected to the company website" in page_text or "being redirected" in page_text:
        return "external"
    # Check for native apply button
    if page.query_selector('#apply-button'):
        return "native"
    return "none"


def _wait_send_enabled(page, timeout_ms: int = 4000) -> bool:
    """Polls until the Send control's wrapper no longer has Naukri's
    'disabled' class. Confirmed real markup (from a debug HTML dump you
    sent): <div id="sendMsg__..." class="send disabled"> wraps the
    clickable <div class="sendMsg">Save</div>. It starts disabled and only
    becomes clickable after Naukri's frontend registers your selection and
    re-renders -- clicking Send before that happens is a silent no-op,
    which is what was causing radio/checkbox answers to never actually save."""
    waited = 0
    step = 300
    while waited <= timeout_ms:
        enabled = safe_evaluate(page, """
            () => {
                const wrapper = document.querySelector('[id^="sendMsg__"]');
                if (!wrapper) return true;  // no wrapper found -- don't block forever on a guess
                return !wrapper.className.includes('disabled');
            }
        """, default=True)
        if enabled:
            return True
        time.sleep(step / 1000)
        waited += step
    return False


def _js_click_send(page) -> bool:
    """Clicks Naukri's screening-chat Send/Save control -- a <div class="sendMsg">,
    not a <button>. A JS click bypasses the chatbot_Overlay div that sits
    visually on top of it and blocks Playwright's normal .click()."""
    return safe_evaluate(page, """
        () => {
            const el = document.querySelector('.sendMsg');
            if (!el) return false;
            el.click();
            return true;
        }
    """, default=False)


def click_native_apply(page) -> bool:
    """Clicks the Apply button and returns whether the click actually
    registered, so the caller can tell 'click failed' apart from 'clicked
    fine, just couldn't confirm success afterward' -- those need different
    handling."""
    return bool(safe_evaluate(page, """
        () => {
            const btn = document.getElementById('apply-button');
            if (btn) { btn.click(); return true; }
            return false;
        }
    """, default=False))


def page_has_stop_signal(page, security_controller: SecurityController = None) -> str | None:
    """
    Check if page has a security stop signal.
    
    Uses SecurityController for unified detection.
    Falls back to legacy STOP_PHRASES for backward compatibility.
    """
    if security_controller is None:
        security_controller = get_security_controller()
    
    try:
        text = page.inner_text("body").lower()
    except Exception:
        return None  # page mid-navigation -- checked again on the next loop iteration
    
    # Use centralized security controller
    event = security_controller.check_page_for_security_signals(
        page_text=text,
        page_url=page.url,
    )
    if event:
        return event.signal
    
    # Legacy fallback
    for phrase in STOP_PHRASES:
        if phrase in text:
            return phrase
    if "login" in page.url and "naukri.com/nlogin" in page.url:
        return "session expired / login prompt"
    return None


def _save_debug_screenshot(page, job_title: str) -> str:
    """Saves a screenshot when the outcome is uncertain, so it can be looked
    at afterward instead of needing to catch it live. Also saves the page's
    HTML for the same reason — a screenshot shows what it looked like, the
    HTML shows exactly why the confirmation-text check missed it."""
    debug_dir = Path("debug_screenshots")
    debug_dir.mkdir(exist_ok=True)
    safe_name = "".join(c if c.isalnum() else "_" for c in (job_title or "unknown"))[:60]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    png_path = debug_dir / f"{safe_name}_{timestamp}.png"
    html_path = debug_dir / f"{safe_name}_{timestamp}.html"
    try:
        page.screenshot(path=str(png_path))
    except Exception as e:
        print(f"  (couldn't save debug screenshot: {e})")
    try:
        html_path.write_text(page.content())
    except Exception as e:
        print(f"  (couldn't save debug HTML: {e})")
    return str(png_path)


def _save_live_screenshot(page, screenshots_dir: Path) -> str:
    """Saves a live screenshot for real-time viewing."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    png_path = screenshots_dir / f"live_{timestamp}.png"
    try:
        page.screenshot(path=str(png_path), full_page=False)
        # Keep only the latest 50 screenshots to avoid disk space issues
        existing_screenshots = sorted(screenshots.glob("live_*.png"))
        while len(existing_screenshots) > 50:
            oldest = existing_screenshots.pop(0)
            try:
                oldest.unlink()
            except:
                pass
        return str(png_path)
    except Exception as e:
        print(f"  (couldn't save live screenshot: {e})")
        return ""


def verify_applied(page) -> bool:
    """Best-effort check that the application actually went through. Confirmed
    real pattern: Naukri shows a green checkmark panel reading
    'Applied to "<job title>"' a few seconds after submit -- checking for
    that prefix specifically, plus a short wait since it isn't instant."""
    try:
        page.wait_for_timeout(3000)  # the confirmation panel takes a moment to appear
    except Exception:
        pass
    try:
        text = page.inner_text("body").lower()
    except Exception:
        return False
    success_phrases = [
        'applied to "', "application sent", "successfully applied",
        "you have applied", "applied successfully",
    ]
    if any(p in text for p in success_phrases):
        return True
    btn = page.query_selector('#apply-button')
    if btn:
        try:
            label = btn.inner_text().strip().lower()
            if label and label != "apply":
                return True
        except Exception:
            pass
    return False


class StopRun(Exception):
    """Something genuinely dangerous or account-risking happened -- CAPTCHA,
    login expired, rate-limit warning. Halts the entire run immediately."""


class SkipJob(Exception):
    """This one listing can't be completed -- logs it and moves to the next
    listing. Does NOT stop the run."""


class ApplicationStats:
    """Tracks application statistics for analytics and insights."""

    def __init__(self):
        self.start_time = datetime.now()
        self.stats = {
            "total_seen": 0,
            "total_qualified": 0,  # Jobs that passed all filters
            "total_filtered": 0,
            "total_applied": 0,
            "total_skipped": 0,
            "total_errors": 0,
            "total_uncertain": 0,
            "total_duplicates_skipped": 0,
            "total_security_stops": 0,
            "by_role": {},
            "by_company": {},
            "by_error_category": {},
            "by_skip_reason": {},
        }
        # Initialize with empty stats file to clear old data
        self._save_to_file()
    
    def record_seen(self, role: str):
        self.stats["total_seen"] += 1
        if role not in self.stats["by_role"]:
            self.stats["by_role"][role] = {"seen": 0, "qualified": 0, "applied": 0, "skipped": 0}
        self.stats["by_role"][role]["seen"] += 1

        # Auto-save for real-time updates (throttle to avoid too many writes)
        if self.stats["total_seen"] % 20 == 0:  # Save every 20 jobs seen
            self.auto_save()
    
    def record_qualified(self, role: str):
        """Record a job that passed all filters (before apply button check)."""
        self.stats["total_qualified"] += 1
        if role not in self.stats["by_role"]:
            self.stats["by_role"][role] = {"seen": 0, "qualified": 0, "applied": 0, "skipped": 0}
        self.stats["by_role"][role]["qualified"] += 1
    
    def record_applied(self, role: str, company: str):
        self.stats["total_applied"] += 1
        if role not in self.stats["by_role"]:
            self.stats["by_role"][role] = {"seen": 0, "applied": 0, "skipped": 0}
        self.stats["by_role"][role]["applied"] += 1

        if company not in self.stats["by_company"]:
            self.stats["by_company"][company] = 0
        self.stats["by_company"][company] += 1

        # Auto-save for real-time updates
        self.auto_save()
    
    def record_skipped(self, role: str, reason: str):
        self.stats["total_skipped"] += 1
        if role not in self.stats["by_role"]:
            self.stats["by_role"][role] = {"seen": 0, "qualified": 0, "applied": 0, "skipped": 0}
        self.stats["by_role"][role]["skipped"] += 1

        # Track duplicates separately
        if "duplicate" in reason.lower():
            self.stats["total_duplicates_skipped"] += 1

        if reason not in self.stats["by_skip_reason"]:
            self.stats["by_skip_reason"][reason] = 0
        self.stats["by_skip_reason"][reason] += 1

        # Auto-save for real-time updates (but throttle for skips to avoid too many writes)
        if self.stats["total_skipped"] % 10 == 0:  # Save every 10 skips
            self.auto_save()
    
    def record_error(self, error_category: str):
        self.stats["total_errors"] += 1
        if error_category not in self.stats["by_error_category"]:
            self.stats["by_error_category"][error_category] = 0
        self.stats["by_error_category"][error_category] += 1
    
    def record_uncertain(self):
        """Record an uncertain application (verification failed)."""
        self.stats["total_uncertain"] += 1
    
    def record_security_stop(self):
        """Record a security stop event."""
        self.stats["total_security_stops"] += 1

    def _save_to_file(self):
        """Save stats to file without calculating end_time or success_rate."""
        import json
        with open(STATS_FILE, "w") as f:
            json.dump(self.stats, f, indent=2)

    def save(self, is_final: bool = False):
        """Save stats to file with optional final calculations."""
        import json
        if is_final:
            self.stats["end_time"] = datetime.now().isoformat()
            self.stats["duration_seconds"] = (datetime.now() - self.start_time).total_seconds()
        self.stats["success_rate"] = (
            (self.stats["total_applied"] / self.stats["total_seen"] * 100)
            if self.stats["total_seen"] > 0 else 0
        )

        with open(STATS_FILE, "w") as f:
            json.dump(self.stats, f, indent=2)

    def auto_save(self):
        """Auto-save stats periodically for real-time updates."""
        self.save(is_final=False)
    
    def print_summary(self):
        duration = (datetime.now() - self.start_time).total_seconds()
        success_rate = (
            (self.stats["total_applied"] / self.stats["total_seen"] * 100) 
            if self.stats["total_seen"] > 0 else 0
        )
        
        print("\n" + "="*60)
        print("APPLICATION STATISTICS SUMMARY")
        print("="*60)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Jobs Found: {self.stats['total_seen']}")
        print(f"Jobs Qualified: {self.stats['total_qualified']}")
        print(f"Jobs Skipped: {self.stats['total_skipped']}")
        print(f"Applications Attempted: {self.stats['total_applied'] + self.stats['total_uncertain']}")
        print(f"Applications Submitted: {self.stats['total_applied']}")
        print(f"Applications Failed: {self.stats['total_errors']}")
        print(f"Applications Uncertain: {self.stats['total_uncertain']}")
        print(f"Duplicates Skipped: {self.stats['total_duplicates_skipped']}")
        print(f"Security Stops: {self.stats['total_security_stops']}")
        print(f"Success rate: {success_rate:.1f}%")
        
        print("\nBy Role:")
        for role, counts in self.stats["by_role"].items():
            qualified = counts.get("qualified", 0)
            print(f"  {role}: seen={counts['seen']}, qualified={qualified}, applied={counts['applied']}, skipped={counts['skipped']}")
        
        if self.stats["by_skip_reason"]:
            print("\nSkip Reasons:")
            for reason, count in sorted(self.stats["by_skip_reason"].items(), key=lambda x: x[1], reverse=True):
                print(f"  {reason}: {count}")
        
        if self.stats["by_error_category"]:
            print("\nError Categories:")
            for category, count in sorted(self.stats["by_error_category"].items(), key=lambda x: x[1], reverse=True):
                print(f"  {category}: {count}")
        
        print("="*60)
        print(f"Statistics saved to {STATS_FILE}")
        print("="*60)
        
        # Send email notification
        try:
            notification_service = get_notification_service()
            notification_service.send_application_summary(
                total_applied=self.stats['total_applied'],
                total_skipped=self.stats['total_skipped'],
                total_errors=self.stats['total_errors'],
                success_rate=success_rate,
                duration_seconds=duration,
                jobs_by_role=self.stats['by_role'],
            )
        except Exception as e:
            print(f"Failed to send notification email: {e}")


def _get_options(page) -> list[dict]:
    """Reads radio/checkbox options in the chat drawer, with their visible labels."""
    return safe_evaluate(page, """
        () => {
            const root = document.querySelector('[class*="chatbot_Drawer"]') || document;
            const inputs = Array.from(root.querySelectorAll('input[type=radio], input[type=checkbox]'));
            return inputs.map((el, idx) => {
                let label = '';
                if (el.id) {
                    const lbl = root.querySelector(`label[for="${el.id}"]`);
                    if (lbl) label = lbl.innerText.trim();
                }
                if (!label) {
                    const parentLabel = el.closest('label');
                    if (parentLabel) label = parentLabel.innerText.trim();
                }
                if (!label && el.nextElementSibling) {
                    label = (el.nextElementSibling.innerText || '').trim();
                }
                return {idx, label, type: el.type};
            });
        }
    """, default=[]) or []


def _click_option(page, idx: int) -> bool:
    return safe_evaluate(page, """
        (idx) => {
            const root = document.querySelector('[class*="chatbot_Drawer"]') || document;
            const inputs = Array.from(root.querySelectorAll('input[type=radio], input[type=checkbox]'));
            if (inputs[idx]) { inputs[idx].click(); return true; }
            return false;
        }
    """, arg=idx, default=False)


def _is_sensitive_field(question: str) -> bool:
    lower_q = question.lower()
    return any(hint in lower_q for hint in SENSITIVE_FIELD_HINTS)


def _auto_decide_option(question: str, options: list[dict], profile: Profile) -> dict | None:
    """Tries to pick the correct option using known profile facts, for
    common Yes/No-style questions. Returns None (never guesses) if nothing
    in the profile clearly answers this specific question -- caller falls
    back to asking you directly rather than risk a wrong click."""
    lower_q = question.lower()
    by_label = {o["idx"]: o["label"].strip().lower() for o in options}

    def find_by_text(text: str):
        for idx, label in by_label.items():
            if label == text.lower():
                return next(o for o in options if o["idx"] == idx)
        return None

    rules = [
        (["relocate", "relocation", "willing to move"],
         "Yes" if profile.data.get("relocate_cities") else "No"),
        (["night shift"], "Yes" if profile.data.get("night_shift_ok") else "No"),
        (["weekend"], "Yes" if profile.data.get("weekend_ok") else "No"),
        (["immediately available", "immediate joiner"],
         "Yes" if profile.data.get("immediately_available") else "No"),
        (["currently employed", "currently working"],
         "Yes" if profile.data.get("current_employer") else "No"),
    ]
    for triggers, desired in rules:
        if any(t in lower_q for t in triggers):
            match = find_by_text(desired)
            if match:
                return match
    return None


def _handle_options_question(page, question: str, profile: Profile, timeout_s: int) -> bool:
    """Returns True if handled (clicked something), raises SkipJob otherwise."""
    options = _get_options(page)
    if not options:
        return False

    stored = learned_answers.get_answer(question)
    if stored:
        for opt in options:
            if opt["label"].strip().lower() == stored.strip().lower():
                _click_option(page, opt["idx"])
                print(f"  (used a remembered answer for: {question[:80]})")
                return True

    auto = _auto_decide_option(question, options, profile)
    if auto:
        _click_option(page, auto["idx"])
        learned_answers.save_answer(question, auto["label"])
        print(f"  (auto-picked '{auto['label']}' from your profile for: {question[:80]})")
        return True

    options_text = "\n".join(f"  {o['idx']}: {o['label']}" for o in options)
    response = ask_user(
        f"Screening question needs a choice:\n{question}\n\nOptions:\n{options_text}\n"
        f"Type the number of your choice (or numbers separated by commas for multi-select):",
        timeout_seconds=timeout_s,
    )
    if response is None:
        raise SkipJob(f"no response for options question: {question[:120]}")

    chosen_raw = [r.strip() for r in response.split(",") if r.strip()]
    matches = []
    for r in chosen_raw:
        try:
            idx = int(r)
            match = next((o for o in options if o["idx"] == idx), None)
        except ValueError:
            match = next((o for o in options if o["label"].strip().lower() == r.lower()), None)
        if match:
            matches.append(match)

    if not matches:
        raise SkipJob(f"couldn't match your response '{response}' to an option: {question[:120]}")

    for match in matches:
        _click_option(page, match["idx"])
    learned_answers.save_answer(question, matches[0]["label"] if len(matches) == 1 else response)
    return True


# If the chat's last message is one of these, it's wrapping up rather than
# asking something new -- stop cleanly instead of trying to draft an answer
# into a box that may no longer exist.
COMPLETION_PHRASES = [
    "thank you", "thanks for your response", "thanks for your time",
    "we will get back", "responses have been recorded", "no further questions",
    "application submitted", "that's all", "all the information we need",
]


def _is_completion_message(text: str) -> bool:
    lower = text.lower()
    return any(p in lower for p in COMPLETION_PHRASES)


def _has_answerable_input(page, timeout_ms: int = 3000) -> bool:
    """Checks for a text box or radio/checkbox to answer. Polls for up to
    timeout_ms instead of checking once -- the previous single-check version
    could wrongly conclude "nothing to answer" if the next question's input
    just hadn't rendered yet after the previous Save click, causing it to
    skip clicking Save on what was actually still a real question."""
    waited = 0
    step = 300
    while waited <= timeout_ms:
        found = safe_evaluate(page, """
            () => !!(document.querySelector('[id^="userInput"], [contenteditable="true"]') ||
                     document.querySelector('input[type=radio], input[type=checkbox]'))
        """, default=False)
        if found:
            return True
        time.sleep(step / 1000)
        waited += step
    return False


def _read_filled_text(page) -> str:
    return safe_evaluate(page, """
        () => {
            const ed = document.querySelector('[id^="userInput"], [contenteditable="true"]');
            return ed ? (ed.innerText || ed.textContent || '').trim() : '';
        }
    """, default="") or ""


def _fill_and_send(page, text: str, question: str):
    """Fills the answer box, VERIFIES the text actually landed before
    clicking Send, then sends. This is the fix for answers going through
    blank: previously Send could fire even if the fill silently failed
    (a timing hiccup, or the box wasn't there), which is what produces
    Naukri's "incomplete information" rejection on the final application."""
    _fill_freetext(page, text)
    time.sleep(0.4)
    filled = _read_filled_text(page)
    if not filled:
        _fill_freetext(page, text)  # one retry -- could be a focus/timing hiccup
        time.sleep(0.6)
        filled = _read_filled_text(page)
    if not filled:
        raise SkipJob(f"couldn't confirm the answer registered before sending: {question[:120]}")
    _wait_send_enabled(page)  # same disabled-until-registered pattern as the options branch
    _js_click_send(page)
    time.sleep(2.0)  # give Naukri's backend a moment to actually save it


def answer_screening_chat(page, profile: Profile, job_context: str, timeout_s: int):
    """Handles Naukri's post-apply screening chat drawer, if it appears."""
    answers = profile.answer_library()
    try:
        # Broadened on purpose: a pure radio/checkbox question has no text
        # box at all, so waiting only for contenteditable was causing the
        # function to give up immediately on those questions, thinking
        # there was no screening chat when there actually was one.
        page.wait_for_selector(
            '[contenteditable="true"], [contenteditable=""], '
            'input[type=radio], input[type=checkbox], .botMsg',
            timeout=4000,
        )
    except PWTimeout:
        return  # no screening chat for this listing

    for _ in range(15):
        stop = page_has_stop_signal(page)
        if stop:
            raise StopRun(f"stop signal during screening chat: {stop}")

        bubbles = page.query_selector_all('.botMsg')
        if not bubbles:
            break
        try:
            question = bubbles[-1].inner_text().strip()
        except Exception:
            break  # page likely navigated away mid-read; treat as chat finished
        if not question:
            break

        if _is_completion_message(question):
            time.sleep(1.5)  # let the "Applied" confirmation redirect begin before we check for it
            break  # chat is wrapping up, not asking a new question

        if not _has_answerable_input(page):
            break  # nothing to fill or click here — informational message only

        options = _get_options(page)
        if options:
            _handle_options_question(page, question, profile, timeout_s)
            if not _wait_send_enabled(page):
                raise SkipJob(f"Send button stayed disabled after selecting an option "
                               f"(selection may not have registered): {question[:120]}")
            _js_click_send(page)
            time.sleep(2.0)
            continue

        stored = learned_answers.get_answer(question)
        if stored:
            _fill_and_send(page, stored, question)
            print(f"  (used a remembered answer for: {question[:80]})")
            continue

        lower_q = question.lower()
        answered = False
        for key, phrases in TRIGGER_PHRASES.items():
            if key not in answers:
                continue
            if any(phrase in lower_q for phrase in phrases):
                _fill_and_send(page, str(answers[key]), question)
                answered = True
                break

        if answered:
            continue

        if _is_sensitive_field(question):
            response = ask_user(f"Screening question (personal detail):\n{question}", timeout_seconds=timeout_s)
            if response is None:
                raise SkipJob(f"no response for sensitive field: {question[:120]}")
            _fill_and_send(page, response, question)
            learned_answers.save_answer(question, response)
            continue

        draft = llm.draft_answer(question, profile.data, job_context)
        if draft.startswith("[NEEDS_HUMAN_INPUT"):
            response = ask_user(f"Screening question (AI couldn't answer from your profile):\n{question}",
                                 timeout_seconds=timeout_s)
            if response is None:
                raise SkipJob(f"no response for: {question[:120]}")
            _fill_and_send(page, response, question)
            learned_answers.save_answer(question, response)
        else:
            _fill_and_send(page, draft, question)


def _fill_freetext(page, text: str):
    safe_evaluate(page, """
        (text) => {
            const ed = document.querySelector('[id^="userInput"], [contenteditable="true"]');
            if (!ed) return;
            ed.focus();
            document.execCommand('insertText', false, text);
        }
    """, arg=text)


def run():
    profile = Profile.load()
    if not Path(SESSION_FILE).exists():
        raise SystemExit(f"{SESSION_FILE} not found. Run: python login_capture.py naukri")

    # Load safety configuration
    safety_config = SafetyConfig.load(profile.data)
    validation_errors = safety_config.validate()
    if validation_errors:
        print("Safety configuration errors:")
        for error in validation_errors:
            print(f"  - {error}")
        raise SystemExit("Invalid safety configuration")

    # Initialize security components
    security_controller = get_security_controller()
    state_machine = get_application_state_machine()
    retry_handler = get_retry_handler(safety_config.max_retries)
    limiter = get_application_limiter(
        max_per_run=profile.stop_after_n_applications,
        max_per_hour=safety_config.max_applications_per_hour,
        max_per_day=safety_config.max_applications_per_day,
    )

    # Check for emergency stop
    if safety_config.emergency_stop_enabled and security_controller.check_emergency_stop():
        print("Emergency stop file detected. Clear it to continue.")
        print("To clear: remove the STOP_AUTOMATION file or run with --clear-emergency-stop")
        raise SystemExit("Emergency stop active")

    # Check for uncertain applications from previous crash
    uncertain_apps = state_machine.get_uncertain_applications()
    if uncertain_apps:
        print("\n" + "="*60)
        print("UNCERTAIN APPLICATIONS FROM PREVIOUS RUN")
        print("="*60)
        for app in uncertain_apps:
            print(f"  {app.title} @ {app.company} - {app.reason}")
        print("These applications were not confirmed. Please check manually.")
        print("They will NOT be automatically resubmitted.")
        print("="*60)

    # Check for security-stopped applications
    security_stopped_apps = state_machine.get_security_stopped_applications()
    if security_stopped_apps:
        print("\n" + "="*60)
        print("SECURITY-STOPPED APPLICATIONS FROM PREVIOUS RUN")
        print("="*60)
        for app in security_stopped_apps:
            print(f"  {app.title} @ {app.company} - {app.reason}")
        print("These applications were stopped due to security events.")
        print("Please review the security events log before continuing.")
        print("="*60)

    # Check for dry-run mode
    dry_run = profile.data.get("dry_run", False)
    if dry_run:
        print("="*60)
        print("DRY-RUN MODE ENABLED")
        print("No actual applications will be submitted.")
        print("This is a simulation to test configuration and filtering.")
        print("="*60)

    human_timeout = profile.data.get("human_input_timeout_seconds", 120)
    max_pages = profile.data.get("max_pages_per_role", 5)

    # Get random delay settings (default: 10-60 seconds for more human-like behavior)
    delay_min = profile.data.get("random_delay_min_seconds", 10)
    delay_max = profile.data.get("random_delay_max_seconds", 60)

    # Get screen capture settings
    enable_screen_capture = profile.data.get("enable_screen_capture", True)
    screen_capture_interval = profile.data.get("screen_capture_interval", 2)  # seconds

    # Create screenshots directory
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)

    # Initialize statistics tracking
    stats = ApplicationStats()

    # Screen capture management (no threading - Playwright doesn't support it)
    last_screenshot_time = 0

    applied = 0
    with sync_playwright() as p:
        browser_mode = profile.data.get("browser_mode", "visible")
        # Force visible mode for screen capture
        if enable_screen_capture:
            browser_mode = "visible"
            print("Screen capture enabled - forcing visible browser mode")

        if browser_mode == "headless":
            browser = p.chromium.launch(
                headless=True,
                slow_mo=150,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
        elif browser_mode == "minimized":
            browser = p.chromium.launch(
                headless=False,
                slow_mo=150,
                args=[
                    "--start-minimized",
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
        else:
            browser = p.chromium.launch(
                headless=False,
                slow_mo=150,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )

        context = browser.new_context(storage_state=SESSION_FILE)
        page = context.new_page()
        # Setup human-like context settings (pass page for viewport)
        setup_human_like_context(context, page)

        if enable_screen_capture:
            print(f"Screen capture enabled (manual capture at key points)")

        # Global two-phase approach: Phase 1 (7 days) across ALL roles, then Phase 2 (30 days) across ALL roles
        for phase, freshness_days in enumerate([profile.job_freshness_days_phase1, profile.job_freshness_days_phase2], 1):
            if applied >= profile.stop_after_n_applications:
                break

            # Skip Phase 2 if already at capacity after Phase 1
            if phase == 2 and applied >= profile.stop_after_n_applications:
                print(f"\n=== Skipping Phase 2 (capacity reached: {applied}/{profile.stop_after_n_applications}) ===")
                break

            phase_label = f"Phase {phase} (last {freshness_days} days)"
            print(f"\n{'='*60}")
            print(f"GLOBAL {phase_label} - SEARCHING ALL ROLES")
            print(f"{'='*60}")

            for role in profile.target_roles:
                if applied >= profile.stop_after_n_applications:
                    break

                # Check emergency stop before each role
                if safety_config.emergency_stop_enabled and _emergency_stop_requested:
                    print("Emergency stop requested by user")
                    break

                slug = role.lower().replace(" ", "-")
                exp_param = int(profile.total_experience_years)
                seen_job_ids = set()
                stopped_entirely = False

                print(f"\n=== {role} - {phase_label} ===")

                for page_no in range(1, max_pages + 1):
                    if applied >= profile.stop_after_n_applications:
                        break

                    # Check emergency stop before each page
                    if safety_config.emergency_stop_enabled and _emergency_stop_requested:
                        print("Emergency stop requested by user")
                        break

                    # Confirmed pattern: Naukri appends "-N" directly to the slug
                    # for page N (page 1 has no suffix), e.g.
                    # azure-data-engineer-jobs-2 for page 2.
                    page_suffix = "" if page_no == 1 else f"-{page_no}"
                    url = (
                        f"https://www.naukri.com/{slug}-jobs{page_suffix}"
                        f"?experience={exp_param}"
                        f"&jobAge={freshness_days}"
                    )
                    print(f"\n--- Searching: {role}, page {page_no} ({url}) ---")
                    try:
                        page.goto(url)
                        page.wait_for_selector('.srp-jobtuple-wrapper[data-job-id]', timeout=10000)
                    except PWTimeout:
                        pass
                    except Exception as e:
                        print(f"  (navigation error, treating as end of results for this phase: {e})")
                        break
                    random_delay(1, 2, "page load")

                    # Pre-action safety check
                    stop = page_has_stop_signal(page, security_controller)
                    if stop:
                        print(f"STOPPING: {stop}")
                        error_cat = categorize_error(stop)
                        log_row([datetime.now(), "naukri", "-", "-", "stopped", stop, error_cat])
                        stats.record_error(error_cat)
                        
                        # Log security event
                        event = security_controller.check_page_for_security_signals(
                            page_text=page.inner_text("body").lower(),
                            page_url=page.url,
                        )
                        if event:
                            security_controller.log_security_event(event)
                        
                        stopped_entirely = True
                        break

                    cards = enumerate_cards(page)
                    new_cards = [c for c in cards if c.get("jobId") not in seen_job_ids]
                    print(f"Found {len(cards)} job cards ({len(new_cards)} new) on page {page_no}.")

                    if not new_cards:
                        print(f"No new listings on page {page_no} -- treating as end of {phase_label}.")
                        break

                    for card in new_cards:
                        seen_job_ids.add(card.get("jobId"))
                        stats.record_seen(role)
                        
                        if applied >= profile.stop_after_n_applications:
                            break

                        # Check emergency stop before each job
                        if safety_config.emergency_stop_enabled and _emergency_stop_requested:
                            print("Emergency stop requested by user")
                            break

                        # Check application limits
                        if not limiter.can_submit():
                            print("Application limit reached. Stopping.")
                            stopped_entirely = True
                            break

                        # Duplicate check
                        is_duplicate, existing_record = state_machine.is_duplicate(
                            job_id=card.get("jobId"),
                            job_url=card.get("href"),
                            company=card.get("company"),
                            title=card.get("title"),
                        )
                        if is_duplicate:
                            stats.record_skipped(role, "duplicate application")
                            log_row([datetime.now(), "naukri", card.get("title"),
                                      card.get("company"), "skipped", "duplicate application", "duplicate"])
                            print(f"Skipped: {card.get('title')} @ {card.get('company')} — duplicate application")
                            continue

                        # Check if job already has a record (from previous run)
                        existing = state_machine.get_record(card.get("jobId"))
                        if existing and existing.state in [ApplicationState.SKIPPED, ApplicationState.SUBMITTED, ApplicationState.FAILED, ApplicationState.UNCERTAIN]:
                            # Skip jobs that are already in terminal states
                            stats.record_skipped(role, f"already {existing.state}")
                            print(f"Skipped: {card.get('title')} @ {card.get('company')} — already {existing.state}")
                            continue

                        # Create application record (only if not already exists)
                        if not existing:
                            state_machine.create_record(
                                job_id=card.get("jobId"),
                                job_url=card.get("href"),
                                title=card.get("title"),
                                company=card.get("company"),
                                source="naukri",
                            )
                        state_machine.transition_record(card.get("jobId"), ApplicationState.FILTERED)

                        ok, reason = passes_filters(card, profile, role)
                        if not ok:
                            state_machine.transition_record(card.get("jobId"), ApplicationState.SKIPPED, reason)
                            stats.record_skipped(role, reason)
                            error_cat = categorize_error(reason)
                            log_row([datetime.now(), "naukri", card.get("title"),
                                      card.get("company"), "skipped", reason, error_cat])
                            print(f"Skipped: {card.get('title')} @ {card.get('company')} — {reason}")
                            continue

                        # Job passed all filters - increment qualified count
                        stats.record_qualified(role)
                        print(f"  [DEBUG] [OK] Job PASSED all filters: {card.get('title')} @ {card.get('company')}")

                        try:
                            if dry_run:
                                print(f"[DRY-RUN] Would apply to: {card.get('title')} @ {card.get('company')}")
                                state_machine.transition_record(card.get("jobId"), ApplicationState.SUBMITTED)
                                stats.record_applied(role, card.get("company"))
                                applied += 1
                                log_row([datetime.now(), "naukri", card.get("title"),
                                          card.get("company"), "dry_run_applied", "", ""])
                                print(f"[DRY-RUN] Applied: {card.get('title')} @ {card.get('company')} ({applied} total)")
                                random_delay(delay_min, delay_max, "next application")
                                continue

                            state_machine.transition_record(card.get("jobId"), ApplicationState.OPENED)
                            
                            # Navigate to job page with retry
                            def navigate_to_job():
                                enhanced_page_navigation(page, card["href"])
                                random_delay(2, 3, "page navigation")
                                # Random mouse movement for natural behavior
                                if random.random() < 0.3:
                                    random_mouse_movement(page)
                                # Capture screenshot after navigation if enabled
                                if enable_screen_capture:
                                    _save_live_screenshot(page, screenshots_dir)
                            
                            retry_handler.execute_with_retry(navigate_to_job, "job navigation")

                            # Pre-action safety check
                            stop = page_has_stop_signal(page, security_controller)
                            if stop:
                                state_machine.transition_record(card.get("jobId"), ApplicationState.SECURITY_STOP, stop)
                                raise StopRun(f"stop signal: {stop}")

                            # Check for external apply immediately after navigation
                            apply_state = check_apply_button(page)
                            print(f"  [DEBUG] Apply button state: {apply_state}")
                            if apply_state == "external":
                                state_machine.transition_record(card.get("jobId"), ApplicationState.SKIPPED, "external apply (company website)")
                                stats.record_skipped(role, "external apply (company website)")
                                log_row([datetime.now(), "naukri", card.get("title"),
                                          card.get("company"), "skipped", "external apply (company website)", "external_apply"])
                                print(f"Skipped: {card.get('title')} @ {card.get('company')} — external apply (company website)")
                                continue
                            if apply_state == "none":
                                state_machine.transition_record(card.get("jobId"), ApplicationState.SKIPPED, "no apply button on job page")
                                stats.record_skipped(role, "no apply button on job page")
                                log_row([datetime.now(), "naukri", card.get("title"),
                                          card.get("company"), "skipped", "no apply button on job page", "ui_element"])
                                print(f"Skipped: {card.get('title')} @ {card.get('company')} — no apply button on job page")
                                continue

                            state_machine.transition_record(card.get("jobId"), ApplicationState.APPLY_STARTED)
                            
                            clicked = click_native_apply(page)
                            if not clicked:
                                state_machine.transition_record(card.get("jobId"), ApplicationState.FAILED, "apply click failed", "ui_element")
                                stats.record_skipped(role, "apply click failed")
                                log_row([datetime.now(), "naukri", card.get("title"),
                                          card.get("company"), "skipped", "apply button click didn't register", "ui_element"])
                                print(f"Skipped: {card.get('title')} @ {card.get('company')} — apply click didn't register")
                                continue
                            random_delay(2, 3, "after apply click")

                            # Capture screenshot after apply click if enabled
                            if enable_screen_capture:
                                _save_live_screenshot(page, screenshots_dir)

                            state_machine.transition_record(card.get("jobId"), ApplicationState.SCREENING)
                            answer_screening_chat(page, profile, f"{card.get('title')} at {card.get('company')}",
                                                   human_timeout)
                            random_delay(1, 2, "after screening chat")

                            state_machine.transition_record(card.get("jobId"), ApplicationState.SUBMISSION_ATTEMPTED)
                            
                            if verify_applied(page):
                                # Check application limits before recording
                                if limiter.record_application():
                                    state_machine.transition_record(card.get("jobId"), ApplicationState.SUBMITTED)
                                    applied += 1
                                    stats.record_applied(role, card.get("company"))
                                    log_row([datetime.now(), "naukri", card.get("title"),
                                              card.get("company"), "applied", "", ""])
                                    print(f"Applied: {card.get('title')} @ {card.get('company')} ({applied} total)")
                                else:
                                    state_machine.transition_record(card.get("jobId"), ApplicationState.FAILED, "limit reached", "limit")
                                    print(f"Limit reached after submission: {card.get('title')} @ {card.get('company')}")
                                    stopped_entirely = True
                                    break
                            else:
                                state_machine.transition_record(card.get("jobId"), ApplicationState.UNCERTAIN, "verification failed", "verification")
                                stats.record_skipped(role, "verification failed")
                                stats.record_uncertain()
                                if safety_config.save_debug_artifacts:
                                    shot_path = _save_debug_screenshot(page, card.get("title"))
                                else:
                                    shot_path = "debug artifacts disabled"
                                log_row([datetime.now(), "naukri", card.get("title"),
                                          card.get("company"), "uncertain",
                                          f"couldn't confirm submission — screenshot saved to {shot_path}", "verification"])
                                print(f"UNCERTAIN: {card.get('title')} @ {card.get('company')} — "
                                      f"couldn't confirm the application actually went through. Check it manually.")

                        except SkipJob as e:
                            state_machine.transition_record(card.get("jobId"), ApplicationState.SKIPPED, str(e))
                            stats.record_skipped(role, str(e))
                            error_cat = categorize_error(str(e))
                            log_row([datetime.now(), "naukri", card.get("title"),
                                      card.get("company"), "skipped", str(e), error_cat])
                            print(f"Skipped: {card.get('title')} @ {card.get('company')} — {e}")
                            continue

                        except StopRun as e:
                            state_machine.transition_record(card.get("jobId"), ApplicationState.SECURITY_STOP, str(e), "security")
                            stats.record_error(categorize_error(str(e)))
                            stats.record_security_stop()
                            print(f"STOPPING: {e}")
                            log_row([datetime.now(), "naukri", card.get("title"),
                                      card.get("company"), "stopped", str(e), categorize_error(str(e))])
                            
                            # Log security event
                            event = security_controller.check_page_for_security_signals(
                                page_text=page.inner_text("body").lower(),
                                page_url=page.url,
                                job_id=card.get("jobId"),
                                company=card.get("company"),
                            )
                            if event:
                                security_controller.log_security_event(event)

                            # Stop screen capture
                            if enable_screen_capture:
                                screen_capture_active.clear()
                                if screen_capture_thread:
                                    screen_capture_thread.join(timeout=2)

                            browser.close()
                            stats.save(is_final=True)
                            state_machine._save()
                            limiter.print_status()
                            stats.print_summary()
                            return

                        except Exception as e:
                            # Anything unexpected (stray Playwright errors, torn-down
                            # page contexts, etc.) -- log it and move to the next
                            # listing instead of crashing the whole run.
                            state_machine.transition_record(card.get("jobId"), ApplicationState.FAILED, str(e), categorize_error(str(e)))
                            stats.record_error(categorize_error(str(e)))
                            error_cat = categorize_error(str(e))
                            log_row([datetime.now(), "naukri", card.get("title"),
                                      card.get("company"), "skipped", f"unexpected error: {e}", error_cat])
                            print(f"Skipped (unexpected error): {card.get('title')} @ {card.get('company')} — {e}")
                            continue

                        random_delay(delay_min, delay_max, "next application")

                    if stopped_entirely:
                        break

            if stopped_entirely:
                break

        # Stop screen capture
        if enable_screen_capture:
            screen_capture_active.clear()
            if screen_capture_thread:
                screen_capture_thread.join(timeout=2)

        browser.close()

    stats.save(is_final=True)
    state_machine._save()
    limiter.print_status()
    stats.print_summary()
    print(f"\nDone. {applied} applications submitted this run. See {LOG_FILE} for the full log.")


if __name__ == "__main__":
    run()
