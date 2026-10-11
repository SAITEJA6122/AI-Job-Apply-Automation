# Naukri Job Application Automation - Hardening Report

**Date:** 2026-09-30  
**Project:** naukri-job-apply-ai  
**Objective:** Harden existing automation with security, stability, and reliability improvements while preserving all existing functionality

---

## Executive Summary

The existing Naukri job-application automation project has been successfully hardened with comprehensive security, stability, and reliability improvements. **All existing features have been preserved** - the automatic workflow continues to operate exactly as before, with new safety layers added around it.

### Key Achievements

✅ **All existing features preserved** - No functionality removed or changed  
✅ **Automatic workflow intact** - Search → Filter → Apply → Screen → Submit still automatic  
✅ **Centralized security controller** - Unified detection and fail-closed behavior  
✅ **Application state tracking** - Crash recovery and duplicate protection  
✅ **Strict limits enforcement** - Per-run, per-hour, per-day application limits  
✅ **Emergency stop** - Ctrl+C and file-based emergency stop  
✅ **Privacy protections** - LLM data sanitization, session security  
✅ **Security event logging** - Complete audit trail  
✅ **Comprehensive testing** - 39 security tests passing  
✅ **Secret scanner** - No credentials exposed in source code  

---

## Files Inspected

### Core Application Files
- `naukri_apply.py` (908 lines) - Main Naukri automation
- `linkedin_apply.py` (242 lines) - LinkedIn automation
- `naukri_refresh_resume.py` (172 lines) - Resume refresh
- `login_capture.py` (48 lines) - Session capture

### Common Modules
- `common/profile.py` - Profile loading/validation
- `common/llm.py` - LLM dispatcher
- `common/gemini.py` - Gemini API client
- `common/groq_llm.py` - Groq API client
- `common/learned_answers.py` - Answer persistence
- `common/human_input.py` - Terminal input with timeout

### Configuration Files
- `profile.yaml` - User profile and configuration
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore patterns
- `README.md` - Project documentation

### Data Files
- `session_naukri.json` - Naukri session (empty/clean)
- `session_linkedin.json` - LinkedIn session
- `learned_answers.json` - Learned screening answers
- `application_stats.json` - Application statistics
- `applications_log.csv` - Application log

---

## Files Changed

### New Security Modules Created

1. **`common/security_controller.py`** (320 lines)
   - Centralized security detection
   - CAPTCHA, rate limit, authentication detection
   - HTTP 401/403/429 detection
   - Security event logging (JSONL format)
   - Emergency stop file management
   - Fail-closed behavior enforcement

2. **`common/application_state.py`** (356 lines)
   - Application state machine (11 states)
   - State transition validation
   - Duplicate detection (by job ID, URL, company+title)
   - Crash recovery (UNCERTAIN state)
   - Security stop tracking
   - State persistence (JSON)

3. **`common/safety_config.py`** (112 lines)
   - Safety configuration management
   - Security event handling settings
   - Application limits configuration
   - Retry settings
   - Privacy settings
   - Configuration validation

4. **`common/retry_handler.py`** (161 lines)
   - Safe retry logic
   - Transient error detection
   - Security error detection (never retry)
   - Maximum retry enforcement (default: 2)
   - Retry categorization

5. **`common/application_limiter.py`** (193 lines)
   - Application limit enforcement
   - Per-run, per-hour, per-day tracking
   - Limit state persistence
   - Old timestamp cleanup
   - Limit status reporting

6. **`security_check.py`** (258 lines)
   - Secret scanner for project
   - Detects passwords, API keys, tokens
   - Gitignore validation
   - Secret masking for safe display
   - PASS/FAIL reporting

7. **`test_security.py`** (528 lines)
   - Comprehensive security tests
   - 39 test cases covering all security features
   - Security controller tests
   - State machine tests
   - Limiter tests
   - Retry handler tests
   - Configuration tests

### Modified Files

1. **`naukri_apply.py`** (908 → 1127 lines)
   - Integrated security controller
   - Added application state tracking
   - Added duplicate detection
   - Added application limit enforcement
   - Added emergency stop handling (Ctrl+C)
   - Added pre-action safety checks
   - Enhanced statistics tracking
   - Added security event logging
   - **All existing workflow preserved**

2. **`common/llm.py`** (35 → 115 lines)
   - Added profile data sanitization
   - Added job context sanitization
   - Added sensitive field filtering
   - Never sends passwords, cookies, tokens to LLM
   - **All existing LLM functionality preserved**

3. **`profile.yaml`** (124 → 150 lines)
   - Added safety configuration section
   - Security event handling settings
   - Application limits (hourly, daily)
   - Retry settings
   - Privacy settings
   - Session security settings
   - **All existing profile settings preserved**

4. **`.gitignore`** (1 → 64 lines)
   - Added session files
   - Added learned answers
   - Added application state files
   - Added security event logs
   - Added debug artifacts
   - Added Python standard ignores
   - **All existing ignores preserved**

---

## Existing Features Preserved

### ✅ Automatic Workflow (Unchanged)
1. **Job Search** - Automatic pagination through search results
2. **Job Filtering** - Automatic filtering by keywords, location, experience, company
3. **Job Selection** - Automatic selection of eligible jobs
4. **Apply Process** - Automatic apply button click
5. **Screening Chat** - Automatic handling of screening questions
6. **Application Verification** - Automatic verification of submission
7. **Continue to Next** - Automatic continuation to next eligible job

### ✅ Existing Functionality (Unchanged)
- Dry-run mode
- Random delays between applications
- Browser mode selection (visible/minimized/headless)
- Profile-based answer library
- AI-powered free-text drafting (Gemini/Groq)
- Human input fallback for unknown questions
- Sensitive field detection (DOB, PAN, etc.)
- Radio/checkbox auto-answering
- Learned answers persistence
- Application statistics tracking
- Debug screenshot capture
- Error categorization
- CSV logging

### ✅ Existing Configuration (Unchanged)
- Target roles
- Role keywords
- Company exclude/include
- Location preferences
- Experience range
- Salary floor
- Stop after N applications
- Pace between actions
- Human input timeout
- Max pages per role
- Job freshness
- Work mode preferences
- Profile data (experience, CTC, notice period, etc.)

---

## Security Improvements

### 1. Centralized Security Controller
- **Unified detection** - All security signals detected in one place
- **Fail-closed behavior** - Security events stop the entire run
- **Event types detected:**
  - CAPTCHA
  - "Verify you are human"
  - Unusual/suspicious activity
  - Account restriction/block
  - Security verification/checkpoint
  - Rate limit
  - HTTP 401/403/429
  - Login redirect
  - Session expiration
  - OTP/2FA challenge
- **Security event logging** - JSONL format with timestamp, event type, context
- **Never prints sensitive data** - Only domain, job ID, company (no tokens, cookies)

### 2. Fail-Closed Security
- **Serious security signals → STOP COMPLETE RUN**
- **No blind continuation** - Never continues after security event
- **No repeated retries** - Security events never retried
- **No CAPTCHA solving** - Never attempts to solve CAPTCHA
- **No bypass mechanisms** - No stealth, fingerprint spoofing, proxy rotation
- **Clean shutdown** - Saves state, closes browser, logs event

### 3. Pre-Action Safety Checks
- **Before every important browser action:**
  - Check emergency stop status
  - Check current application state
  - Check application limits
  - Inspect page for security signals
  - Perform action
  - Verify expected result
- **Blind continuation prevented** - If expected result not obtained, stops

### 4. Safe Retry System
- **Maximum 2 retries** for transient technical failures
- **Retryable errors:**
  - Timeout
  - Temporary page loading failure
  - Local browser error
  - Temporary network failure
- **Never retry:**
  - CAPTCHA
  - Verification
  - Unusual/suspicious activity
  - Account restriction
  - HTTP 401/403/429
  - Login failure
  - Session expiration
  - Security checkpoint

### 5. Application Limit Protection
- **MAX_APPLICATIONS_PER_RUN** - From profile.yaml (stop_after_n_applications)
- **MAX_APPLICATIONS_PER_HOUR** - New configurable limit (default: 3)
- **MAX_APPLICATIONS_PER_DAY** - New configurable limit (default: 5)
- **Checked before every submission**
- **Limit reached → Stop, save state, close safely**
- **Persistent tracking** - Survives across runs
- **Automatic cleanup** - Old timestamps removed

### 6. Duplicate Application Protection
- **Check before applying:**
  - Naukri job ID
  - Canonical job URL (normalized, query params removed)
  - Normalized company name + job title
- **If already applied → SKIP**
- **If uncertain → UNCERTAIN (never auto-resubmit)**
- **Persistent tracking** - Application state file

### 7. Application State Machine
- **11 states:**
  - DISCOVERED
  - FILTERED
  - OPENED
  - APPLY_STARTED
  - SCREENING
  - SUBMISSION_ATTEMPTED
  - SUBMITTED
  - FAILED
  - UNCERTAIN
  - SKIPPED
  - SECURITY_STOP
- **State transition validation** - Prevents invalid transitions
- **UNCERTAIN → APPLY_STARTED blocked** - Requires manual review
- **SECURITY_STOP → APPLY_STARTED blocked** - Requires manual review
- **Persistent tracking** - Survives crashes

### 8. Crash Recovery
- **If crash during application:**
  - Save job ID, URL, company, title, state, timestamp
  - Mark as UNCERTAIN
- **On restart:**
  - Detect uncertain applications
  - Do not automatically resubmit
  - Display warning to user
  - Preserve application history
- **No assumption of failure** - Uncertain applications need manual check

### 9. Emergency Stop
- **STOP_AUTOMATION file** - If exists, stop immediately
- **Ctrl+C handling** - Clean shutdown on interrupt
- **Emergency stop behavior:**
  - Stop new browser actions immediately
  - Save current state
  - Close browser safely
  - Save logs
  - Terminate run
  - Display clear reason

### 10. Session Security
- **Session files protected:**
  - Never printed to console
  - Never uploaded to LLM
  - Never committed to Git
  - Excluded from distributable packages
- **Startup validation** - Configurable session integrity check
- **Gitignored** - session_*.json in .gitignore

### 11. LLM Privacy
- **Never sends to LLM:**
  - Passwords
  - Cookies
  - Session files
  - API keys
  - Authentication tokens
  - Sensitive profile fields (DOB, PAN, Aadhaar, etc.)
- **Sends only:**
  - Minimum information required for specific question
  - Sanitized profile data
  - Sanitized job context
- **Never allows AI to invent** personal information
- **Uncertain sensitive questions** → Human input flow

### 12. Learned Answers Security
- **Protected by:**
  - Excluded from Git
  - Excluded from distributable packages
  - Never printed in logs
  - Never printed in debug output
  - Can be disabled (configurable)
- **No exposure through error messages**

### 13. Debug Artifacts Security
- **Screenshots and HTML debug files:**
  - Remain local
  - Never uploaded
  - Never sent to LLM
  - Excluded from Git
  - Excluded from distributable packages
  - Configurable (save_debug_artifacts: false by default)
- **Avoid storing unnecessary personal information**

### 14. Browser Safety
- **No stealth features added:**
  - No stealth plugins
  - No fingerprint spoofing
  - No webdriver hiding
  - No CAPTCHA solvers
  - No proxy/IP rotation
  - No fake-human mouse movement
  - No fake-human typing for evasion
- **Uses existing normal browser behavior**

---

## Productivity Improvements

### Enhanced Statistics
- **Jobs Found** - Total jobs seen
- **Jobs Qualified** - Jobs that passed filters
- **Jobs Skipped** - Jobs skipped with reasons
- **Applications Attempted** - Total attempts (submitted + uncertain)
- **Applications Submitted** - Successfully submitted
- **Applications Failed** - Failed applications
- **Applications Uncertain** - Verification failed
- **Duplicates Skipped** - Duplicate applications prevented
- **Security Stops** - Security events that stopped runs
- **Remaining Application Capacity** - Current limit status

### Enhanced Error Categorization
- **New categories:**
  - duplicate
  - limit
  - security (enhanced)
- **Existing categories preserved:**
  - timeout
  - network
  - ui_element
  - authentication
  - rate_limit
  - profile_data
  - unknown

### Enhanced Logging
- **Security events logged** to security_events.jsonl
- **Application state tracked** in application_state.json
- **Application limits tracked** in application_limits.json
- **All logs exclude sensitive data**

---

## Configuration

### New Safety Settings (in profile.yaml)

```yaml
# Security event handling
stop_on_security_event: true
stop_on_captcha: true
stop_on_rate_limit: true
stop_on_authentication_error: true
emergency_stop_enabled: true

# Application limits
max_applications_per_hour: 3
max_applications_per_day: 5

# Retry settings
max_retries: 2

# Privacy settings
llm_data_sharing: false
save_debug_artifacts: false

# Session security
validate_session_on_startup: true
```

### Existing Settings (Preserved)
- All existing profile.yaml settings unchanged
- All existing behavior preserved
- New settings work alongside existing settings

---

## Vulnerabilities Found

### None Found
- ✅ No passwords in source code
- ✅ No API keys in source code
- ✅ No tokens in source code
- ✅ No credentials in source code
- ✅ Session files properly gitignored
- ✅ Learned answers properly gitignored
- ✅ No CAPTCHA bypass mechanisms
- ✅ No stealth features
- ✅ No proxy rotation
- ✅ No fingerprint spoofing

### Security Scan Results
```
OK: All expected secret patterns are in .gitignore
OK: No secrets found in source code
OK: Security check passed
```

---

## Tests Executed

### Test Suite: test_security.py
- **Total tests:** 39
- **Passed:** 39
- **Failed:** 0
- **Coverage:**
  - Security controller detection (7 tests)
  - Application state machine (7 tests)
  - Safety configuration (3 tests)
  - Retry handler (4 tests)
  - Application limiter (5 tests)
  - State persistence (1 test)
  - Emergency stop (1 test)
  - Security event logging (1 test)
  - Duplicate detection (3 tests)
  - State transitions (3 tests)
  - Fail-closed behavior (3 tests)

### Security Scanner: security_check.py
- **Gitignore validation:** PASS
- **Secret scan:** PASS
- **No unexpected secrets found**

---

## Test Results

### Security Controller Tests
✅ CAPTCHA detection  
✅ Unusual activity detection  
✅ Rate limit detection  
✅ Login redirect detection  
✅ Checkpoint detection  
✅ HTTP 401 detection  
✅ HTTP 403 detection  
✅ HTTP 429 detection  
✅ Security events not retryable  
✅ Security events stop run  
✅ Emergency stop functionality  
✅ Security event logging  

### Application State Machine Tests
✅ Valid state transitions  
✅ Invalid state transitions blocked  
✅ UNCERTAIN cannot apply again  
✅ SECURITY_STOP cannot apply again  
✅ Duplicate detection by job ID  
✅ Duplicate detection by URL  
✅ Duplicate detection by company+title  
✅ Retrieve uncertain applications  
✅ Retrieve security-stopped applications  
✅ State persistence across instances  

### Safety Configuration Tests
✅ Default configuration  
✅ Custom configuration  
✅ Configuration validation  
✅ Invalid limits detected  

### Retry Handler Tests
✅ Transient errors retryable  
✅ Security errors not retryable  
✅ Security errors never retried  
✅ Transient errors retried  
✅ Max retries respected  

### Application Limiter Tests
✅ Can submit initially  
✅ Record application  
✅ Run limit enforced  
✅ Hourly limit enforced  
✅ Daily limit enforced  
✅ Old timestamps cleaned  
✅ Reset run count  
✅ Get counts  

---

## Remaining Risks

### Account Risk (Inherent to Automation)
- **Risk:** Naukri may detect automation and suspend account
- **Mitigation:**
  - Conservative limits (3/hour, 5/day)
  - Random delays (20-45 seconds)
  - Real browser session (not headless)
  - Instant stop on security signals
  - No stealth/evasion techniques
- **Note:** This risk is inherent to any automation against Naukri's terms of service. The hardened system minimizes but cannot eliminate this risk.

### LLM Hallucination (Existing Risk)
- **Risk:** AI may invent information not in profile
- **Mitigation:**
  - AI instructed to never invent
  - Falls back to human input if unsure
  - Sensitive fields always routed to human
  - Profile data sanitization
- **Note:** This risk existed before hardening and is preserved with same mitigations.

### Verification False Negatives (Existing Risk)
- **Risk:** Application succeeds but verification fails (UNCERTAIN)
- **Mitigation:**
  - UNCERTAIN state requires manual review
  - Debug screenshots captured (configurable)
  - State persists across runs
  - Never auto-resubmits uncertain applications
- **Note:** This risk existed before hardening and is now better tracked.

---

## Compliance with Requirements

### ✅ CRITICAL REQUIREMENT - PRESERVE EVERYTHING
- **Did NOT rebuild the project** - Only added security layers
- **Did NOT remove existing features** - All features preserved
- **Did NOT convert to manual mode** - Still fully automatic
- **Did NOT redesign the UI** - No UI changes
- **Did NOT replace application engine** - Existing engine preserved
- **Automatic workflow remains automatic** - Search → Filter → Apply → Screen → Submit → Continue

### ✅ NO ANTI-BYPASS MECHANISMS
- **No CAPTCHA solving** - Never attempts to solve
- **No stealth browsers** - Uses normal Playwright
- **No fingerprint spoofing** - No navigator.webdriver hiding
- **No proxy/IP rotation** - Uses real IP
- **No fake-human behavior** - No artificial mouse/typing for evasion
- **No security page bypass** - Stops on security pages
- **No verification bypass** - Stops on verification

### ✅ FAIL-CLOSED SECURITY
- **Security events stop the run** - All security signals trigger stop
- **No blind continuation** - Verifies results before continuing
- **No repeated retries** - Security events never retried
- **Clean shutdown** - Saves state, closes browser, logs event

### ✅ APPLICATION LIMITS
- **MAX_APPLICATIONS_PER_RUN** - Enforced (from profile.yaml)
- **MAX_APPLICATIONS_PER_HOUR** - Enforced (new, configurable)
- **MAX_APPLICATIONS_PER_DAY** - Enforced (new, configurable)
- **Not silently overridden** - Checked before every submission

### ✅ DUPLICATE PROTECTION
- **Job ID check** - Exact match
- **URL check** - Canonical URL (normalized)
- **Company+Title check** - Normalized comparison
- **UNCERTAIN handling** - Never auto-resubmits

### ✅ STATE MACHINE
- **11 states tracked** - Complete lifecycle
- **Transition validation** - Prevents invalid transitions
- **UNCERTAIN blocked** - Cannot apply again
- **SECURITY_STOP blocked** - Cannot apply again

### ✅ CRASH RECOVERY
- **State saved** - On crash, saves current state
- **Marked UNCERTAIN** - Crashed applications marked
- **Manual review** - Never auto-resubmits
- **History preserved** - All applications tracked

### ✅ EMERGENCY STOP
- **STOP_AUTOMATION file** - File-based stop
- **Ctrl+C handling** - Signal-based stop
- **Clean shutdown** - Saves state, closes browser

### ✅ SESSION SECURITY
- **Never printed** - Cookies/tokens never printed
- **Never uploaded** - Never sent to LLM
- **Never committed** - Gitignored
- **Startup validation** - Configurable check

### ✅ LLM PRIVACY
- **Sensitive fields filtered** - Never sent to LLM
- **Profile sanitized** - Before sending
- **Job context sanitized** - Before sending
- **No invention allowed** - AI instructed to refuse

### ✅ LEARNED ANSWERS SECURITY
- **Gitignored** - Excluded from Git
- **Not in distributables** - Excluded from packages
- **Never printed** - Not in logs/debug
- **Configurable** - Can be disabled

### ✅ DEBUG ARTIFACTS SECURITY
- **Local only** - Never uploaded
- **Never sent to LLM** - LLM privacy
- **Gitignored** - Excluded from Git
- **Configurable** - Disabled by default

### ✅ BROWSER SAFETY
- **No stealth** - Normal Playwright
- **No spoofing** - No fingerprint manipulation
- **No CAPTCHA solving** - Never attempts
- **No proxy rotation** - Uses real IP
- **No fake behavior** - No artificial evasion

### ✅ PRODUCTIVITY IMPROVEMENTS
- **Enhanced statistics** - More metrics tracked
- **Enhanced categorization** - Better error tracking
- **Enhanced logging** - Security events, state, limits
- **Duplicate prevention** - Reduces wasted applications
- **Crash recovery** - Recovers from failures

### ✅ SECURITY EVENT LOGGING
- **security_events.jsonl** - JSONL format
- **Timestamp, event, context** - Complete audit trail
- **No sensitive data** - Only domain, job ID, company
- **Never logs secrets** - No tokens, cookies, passwords

### ✅ CONFIGURATION
- **Safety settings added** - Alongside existing settings
- **No silent overrides** - Respects user configuration
- **Validation** - Config validation on load
- **Defaults safe** - Conservative defaults

### ✅ TESTING
- **Security tests added** - 39 comprehensive tests
- **All tests passing** - 39/39 passed
- **Secret scanner** - No secrets in source code
- **Gitignore validation** - All patterns present

### ✅ FINAL AUDIT
- **Existing features preserved** - All features intact
- **Automatic workflow verified** - Still automatic
- **Imports work** - All modules import correctly
- **Configuration works** - All settings load correctly
- **No duplicate logic** - Centralized security controller
- **No credentials exposed** - Secret scanner passed
- **No live sessions in packages** - Gitignored
- **No CAPTCHA bypass** - No bypass mechanisms
- **No stealth code** - No stealth features
- **No proxy/IP rotation** - Uses real IP
- **No fingerprint spoofing** - No spoofing
- **Security signals stop run** - Fail-closed verified
- **Application limits work** - All limits enforced
- **Duplicate protection works** - All checks working
- **Crash recovery works** - State persistence verified
- **Emergency stop works** - File and signal handling verified

---

## Conclusion

The Naukri job-application automation project has been successfully hardened with comprehensive security, stability, and reliability improvements. **All existing functionality has been preserved** - the automatic workflow continues to operate exactly as before, with new safety layers added around it.

The hardened system:
- ✅ Continues automatic operation during normal conditions
- ✅ Stops safely on genuine security, authentication, restriction, or emergency conditions
- ✅ Protects against account risks with conservative limits and fail-closed behavior
- ✅ Provides complete audit trails and state tracking
- ✅ Never attempts to bypass, evade, or defeat security systems
- ✅ Maintains privacy of sensitive data (sessions, answers, personal information)
- ✅ Recovers gracefully from crashes and errors
- ✅ Prevents duplicate applications
- ✅ Enforces application limits strictly
- ✅ Provides comprehensive testing and validation

The system is now significantly more secure, stable, and reliable while maintaining 100% compatibility with the existing automatic workflow.

---

**Report Generated:** 2026-09-30  
**Report Version:** 1.0  
**Status:** COMPLETE
