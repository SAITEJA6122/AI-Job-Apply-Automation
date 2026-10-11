"""
Application State Machine

Tracks the state of each job application through the workflow.
Enforces state transitions to prevent unsafe operations.
"""
import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, List


class ApplicationState(Enum):
    """States in the application workflow."""
    DISCOVERED = "discovered"
    FILTERED = "filtered"
    OPENED = "opened"
    APPLY_STARTED = "apply_started"
    SCREENING = "screening"
    SUBMISSION_ATTEMPTED = "submission_attempted"
    SUBMITTED = "submitted"
    FAILED = "failed"
    UNCERTAIN = "uncertain"
    SKIPPED = "skipped"
    SECURITY_STOP = "security_stop"


class ApplicationRecord:
    """Represents a single job application record."""
    
    def __init__(
        self,
        job_id: str,
        job_url: str,
        title: str,
        company: str,
        source: str = "naukri",
    ):
        self.job_id = job_id
        self.job_url = job_url
        self.title = title
        self.company = company
        self.source = source
        self.state = ApplicationState.DISCOVERED
        self.timestamp = datetime.now().isoformat()
        self.updated_timestamp = self.timestamp
        self.reason: Optional[str] = None
        self.error_category: Optional[str] = None
    
    def transition_to(self, new_state: ApplicationState, reason: Optional[str] = None):
        """
        Transition to a new state.
        
        Raises ValueError if the transition is invalid.
        """
        if not self._is_valid_transition(self.state, new_state):
            raise ValueError(
                f"Invalid state transition: {self.state.value} -> {new_state.value}"
            )
        
        self.state = new_state
        self.updated_timestamp = datetime.now().isoformat()
        if reason:
            self.reason = reason
    
    def _is_valid_transition(self, from_state: ApplicationState, to_state: ApplicationState) -> bool:
        """
        Check if a state transition is valid.
        
        Enforces fail-closed behavior:
        - UNCERTAIN cannot transition to APPLY_STARTED (requires manual review)
        - SECURITY_STOP cannot transition to APPLY_STARTED (requires manual review)
        """
        # Allowed transitions
        valid_transitions = {
            ApplicationState.DISCOVERED: [
                ApplicationState.FILTERED,
                ApplicationState.SKIPPED,
                ApplicationState.FAILED,
            ],
            ApplicationState.SKIPPED: [
                ApplicationState.SKIPPED,  # Allow remaining in SKIPPED
            ],
            ApplicationState.SUBMITTED: [
                ApplicationState.SUBMITTED,  # Allow remaining in SUBMITTED
            ],
            ApplicationState.FAILED: [
                ApplicationState.FAILED,  # Allow remaining in FAILED
            ],
            ApplicationState.UNCERTAIN: [
                ApplicationState.UNCERTAIN,  # Allow remaining in UNCERTAIN
            ],
            ApplicationState.SECURITY_STOP: [
                ApplicationState.SECURITY_STOP,  # Allow remaining in SECURITY_STOP
            ],
            ApplicationState.FILTERED: [
                ApplicationState.OPENED,
                ApplicationState.SKIPPED,
                ApplicationState.FAILED,
            ],
            ApplicationState.OPENED: [
                ApplicationState.APPLY_STARTED,
                ApplicationState.SKIPPED,
                ApplicationState.FAILED,
                ApplicationState.UNCERTAIN,
            ],
            ApplicationState.APPLY_STARTED: [
                ApplicationState.SCREENING,
                ApplicationState.SUBMISSION_ATTEMPTED,
                ApplicationState.FAILED,
                ApplicationState.UNCERTAIN,
                ApplicationState.SECURITY_STOP,
            ],
            ApplicationState.SCREENING: [
                ApplicationState.SUBMISSION_ATTEMPTED,
                ApplicationState.FAILED,
                ApplicationState.UNCERTAIN,
                ApplicationState.SECURITY_STOP,
                ApplicationState.SKIPPED,  # Allow skipping if screening fails
                ApplicationState.SCREENING,  # Allow self-transition for re-processing
                ApplicationState.FILTERED,  # Allow transition back to filtered
                ApplicationState.OPENED,  # Allow transition back to opened
            ],
            ApplicationState.SUBMISSION_ATTEMPTED: [
                ApplicationState.SUBMITTED,
                ApplicationState.FAILED,
                ApplicationState.UNCERTAIN,
                ApplicationState.SECURITY_STOP,
            ],
            ApplicationState.SUBMITTED: [
                # Terminal state - no further transitions
            ],
            ApplicationState.FAILED: [
                # Terminal state - no further transitions
            ],
            ApplicationState.UNCERTAIN: [
                # Terminal state - requires manual review
                # CRITICAL: Cannot transition back to APPLY_STARTED
            ],
            ApplicationState.SKIPPED: [
                # Terminal state - no further transitions
            ],
            ApplicationState.SECURITY_STOP: [
                # Terminal state - requires manual review
                # CRITICAL: Cannot transition back to APPLY_STARTED
            ],
        }
        
        return to_state in valid_transitions.get(from_state, [])
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "job_id": self.job_id,
            "job_url": self.job_url,
            "title": self.title,
            "company": self.company,
            "source": self.source,
            "state": self.state.value,
            "timestamp": self.timestamp,
            "updated_timestamp": self.updated_timestamp,
            "reason": self.reason,
            "error_category": self.error_category,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ApplicationRecord":
        """Create from dictionary."""
        record = cls(
            job_id=data["job_id"],
            job_url=data["job_url"],
            title=data["title"],
            company=data["company"],
            source=data.get("source", "naukri"),
        )
        record.state = ApplicationState(data["state"])
        record.timestamp = data["timestamp"]
        record.updated_timestamp = data["updated_timestamp"]
        record.reason = data.get("reason")
        record.error_category = data.get("error_category")
        return record


class ApplicationStateMachine:
    """
    Manages application state tracking and persistence.
    
    Provides:
    - State tracking for each application
    - Duplicate detection
    - Crash recovery
    - State transition validation
    """
    
    def __init__(self, state_file: str = "application_state.json"):
        self.state_file = Path(state_file)
        self._records: Dict[str, ApplicationRecord] = {}
        self._load()
    
    def _load(self):
        """Load state from file."""
        if not self.state_file.exists():
            return
        
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for record_data in data.get("records", []):
                record = ApplicationRecord.from_dict(record_data)
                self._records[record.job_id] = record
        except Exception as e:
            print(f"Warning: Could not load application state: {e}")
    
    def _save(self):
        """Save state to file."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "last_updated": datetime.now().isoformat(),
                "records": [record.to_dict() for record in self._records.values()],
            }
            
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save application state: {e}")
    
    def create_record(
        self,
        job_id: str,
        job_url: str,
        title: str,
        company: str,
        source: str = "naukri",
    ) -> ApplicationRecord:
        """Create a new application record."""
        if job_id in self._records:
            return self._records[job_id]
        
        record = ApplicationRecord(
            job_id=job_id,
            job_url=job_url,
            title=title,
            company=company,
            source=source,
        )
        self._records[job_id] = record
        self._save()
        return record
    
    def get_record(self, job_id: str) -> Optional[ApplicationRecord]:
        """Get an application record by job ID."""
        return self._records.get(job_id)
    
    def transition_record(
        self,
        job_id: str,
        new_state: ApplicationState,
        reason: Optional[str] = None,
        error_category: Optional[str] = None,
    ) -> bool:
        """
        Transition a record to a new state.
        
        Returns True if successful, False if the record doesn't exist
        or the transition is invalid.
        """
        record = self._records.get(job_id)
        if not record:
            return False
        
        try:
            record.transition_to(new_state, reason)
            if error_category:
                record.error_category = error_category
            self._save()
            return True
        except ValueError as e:
            print(f"Invalid state transition for job {job_id}: {e}")
            return False
    
    def is_duplicate(
        self,
        job_id: str,
        job_url: Optional[str] = None,
        company: Optional[str] = None,
        title: Optional[str] = None,
    ) -> tuple[bool, Optional[ApplicationRecord]]:
        """
        Check if a job is a duplicate of a previously applied job.
        
        Returns (is_duplicate, existing_record).
        Checks by:
        1. Exact job ID match
        2. Canonical URL match (normalized)
        3. Normalized company + title match
        """
        # Exact job ID match
        if job_id in self._records:
            record = self._records[job_id]
            if record.state in (ApplicationState.SUBMITTED, ApplicationState.UNCERTAIN):
                return True, record
        
        # Canonical URL match
        if job_url:
            normalized_url = self._normalize_url(job_url)
            for record in self._records.values():
                if self._normalize_url(record.job_url) == normalized_url:
                    if record.state in (ApplicationState.SUBMITTED, ApplicationState.UNCERTAIN):
                        return True, record
        
        # Normalized company + title match
        if company and title:
            normalized_company = self._normalize_text(company)
            normalized_title = self._normalize_text(title)
            for record in self._records.values():
                if (
                    self._normalize_text(record.company) == normalized_company
                    and self._normalize_text(record.title) == normalized_title
                ):
                    if record.state in (ApplicationState.SUBMITTED, ApplicationState.UNCERTAIN):
                        return True, record
        
        return False, None
    
    def get_uncertain_applications(self) -> List[ApplicationRecord]:
        """Get all applications in UNCERTAIN state (crash recovery)."""
        return [
            record for record in self._records.values()
            if record.state == ApplicationState.UNCERTAIN
        ]
    
    def get_security_stopped_applications(self) -> List[ApplicationRecord]:
        """Get all applications in SECURITY_STOP state."""
        return [
            record for record in self._records.values()
            if record.state == ApplicationState.SECURITY_STOP
        ]
    
    def get_statistics(self) -> dict:
        """Get statistics about application states."""
        stats = {state.value: 0 for state in ApplicationState}
        for record in self._records.values():
            stats[record.state.value] += 1
        return stats
    
    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalize URL for comparison."""
        # Remove query parameters and fragments
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".lower()
    
    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text for comparison."""
        return text.lower().strip()


# Global state machine instance
_state_machine = None


def get_application_state_machine(state_file: str = "application_state.json") -> ApplicationStateMachine:
    """
    Get the global application state machine instance.
    """
    global _state_machine
    if _state_machine is None:
        _state_machine = ApplicationStateMachine(state_file)
    return _state_machine
