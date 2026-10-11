"""
Application Limiter

Enforces application limits to protect the account:
- MAX_APPLICATIONS_PER_RUN
- MAX_APPLICATIONS_PER_HOUR
- MAX_APPLICATIONS_PER_DAY

Tracks application counts and enforces limits before each submission.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class ApplicationLimiter:
    """
    Enforces application limits to protect the account.
    
    Tracks:
    - Applications in current run
    - Applications in last hour
    - Applications in last 24 hours
    
    Enforces limits before each application submission.
    """
    
    def __init__(
        self,
        max_per_run: int = 5,
        max_per_hour: int = 3,
        max_per_day: int = 5,
        state_file: str = "application_limits.json",
    ):
        self.max_per_run = max_per_run
        self.max_per_hour = max_per_hour
        self.max_per_day = max_per_day
        self.state_file = Path(state_file)
        
        self.run_count = 0
        self.hourly_timestamps: list[str] = []
        self.daily_timestamps: list[str] = []
        
        self._load()
    
    def _load(self):
        """Load limit state from file."""
        if not self.state_file.exists():
            return
        
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.hourly_timestamps = data.get("hourly_timestamps", [])
            self.daily_timestamps = data.get("daily_timestamps", [])
            
            # Clean up old timestamps on load
            self._cleanup_old_timestamps()
        except Exception as e:
            print(f"Warning: Could not load application limits: {e}")
    
    def _save(self):
        """Save limit state to file."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "last_updated": datetime.now().isoformat(),
                "hourly_timestamps": self.hourly_timestamps,
                "daily_timestamps": self.daily_timestamps,
            }
            
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save application limits: {e}")
    
    def _cleanup_old_timestamps(self):
        """Remove timestamps older than the tracking windows."""
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)
        
        # Clean hourly timestamps
        self.hourly_timestamps = [
            ts for ts in self.hourly_timestamps
            if datetime.fromisoformat(ts) > one_hour_ago
        ]
        
        # Clean daily timestamps
        self.daily_timestamps = [
            ts for ts in self.daily_timestamps
            if datetime.fromisoformat(ts) > one_day_ago
        ]
    
    def record_application(self) -> bool:
        """
        Record an application submission.
        
        Returns True if the application was recorded successfully,
        False if a limit was reached.
        """
        self._cleanup_old_timestamps()
        
        # Check limits before recording
        if not self.can_submit():
            return False
        
        # Record the application
        now = datetime.now().isoformat()
        self.run_count += 1
        self.hourly_timestamps.append(now)
        self.daily_timestamps.append(now)
        
        self._save()
        return True
    
    def can_submit(self) -> bool:
        """
        Check if another application can be submitted.
        
        Returns True if all limits are satisfied, False otherwise.
        """
        self._cleanup_old_timestamps()
        
        # Check run limit
        if self.run_count >= self.max_per_run:
            print(f"  (Limit reached: {self.run_count}/{self.max_per_run} applications this run)")
            return False
        
        # Check hourly limit
        if len(self.hourly_timestamps) >= self.max_per_hour:
            print(f"  (Limit reached: {len(self.hourly_timestamps)}/{self.max_per_hour} applications in last hour)")
            return False
        
        # Check daily limit
        if len(self.daily_timestamps) >= self.max_per_day:
            print(f"  (Limit reached: {len(self.daily_timestamps)}/{self.max_per_day} applications in last 24 hours)")
            return False
        
        return True
    
    def get_counts(self) -> dict:
        """Get current application counts."""
        self._cleanup_old_timestamps()
        return {
            "run_count": self.run_count,
            "hourly_count": len(self.hourly_timestamps),
            "daily_count": len(self.daily_timestamps),
            "max_per_run": self.max_per_run,
            "max_per_hour": self.max_per_hour,
            "max_per_day": self.max_per_day,
            "remaining_run": max(0, self.max_per_run - self.run_count),
            "remaining_hour": max(0, self.max_per_hour - len(self.hourly_timestamps)),
            "remaining_day": max(0, self.max_per_day - len(self.daily_timestamps)),
        }
    
    def reset_run_count(self):
        """Reset the run count (for new runs)."""
        self.run_count = 0
        self._save()
    
    def print_status(self):
        """Print current limit status."""
        counts = self.get_counts()
        print("\n" + "="*60)
        print("APPLICATION LIMITS STATUS")
        print("="*60)
        print(f"This run: {counts['run_count']}/{counts['max_per_run']} ({counts['remaining_run']} remaining)")
        print(f"Last hour: {counts['hourly_count']}/{counts['max_per_hour']} ({counts['remaining_hour']} remaining)")
        print(f"Last 24 hours: {counts['daily_count']}/{counts['max_per_day']} ({counts['remaining_day']} remaining)")
        print("="*60)


# Global limiter instance
_limiter = None


def get_application_limiter(
    max_per_run: int = 5,
    max_per_hour: int = 3,
    max_per_day: int = 5,
    state_file: str = "application_limits.json",
) -> ApplicationLimiter:
    """
    Get the global application limiter instance.
    """
    global _limiter
    if _limiter is None:
        _limiter = ApplicationLimiter(max_per_run, max_per_hour, max_per_day, state_file)
    return _limiter
