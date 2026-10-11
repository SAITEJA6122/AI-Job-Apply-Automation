"""Loads and validates the applicant profile from profile.yaml."""
import yaml
from pathlib import Path


class Profile:
    def __init__(self, data: dict):
        self.data = data

    @classmethod
    def load(cls, path: str = "profile.yaml") -> "Profile":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(
                f"{path} not found. Copy profile.yaml and fill in your real details first."
            )
        with p.open() as f:
            data = yaml.safe_load(f)
        cls._validate(data)
        return cls(data)

    @staticmethod
    def _validate(data: dict):
        # Only validate resume file name as critical
        # Other fields can have defaults
        if not data.get("resume_file_name"):
            # Don't raise error, just log warning
            print("Warning: No resume file specified in profile.yaml")
        
        # Set defaults for missing fields
        data.setdefault("total_experience_years", 0)
        data.setdefault("notice_period_days", 0)
        data.setdefault("current_ctc_lpa", 0)
        data.setdefault("expected_ctc_lpa", 3)

    def __getattr__(self, item):
        if item in self.data:
            return self.data[item]
        raise AttributeError(item)

    @property
    def job_freshness_days_phase1(self) -> int:
        """Phase 1: jobs from last N days (default 7)"""
        return self.data.get("job_freshness_days_phase1", 7)

    @property
    def job_freshness_days_phase2(self) -> int:
        """Phase 2: jobs from last N days (default 30, used after Phase 1 exhausted)"""
        return self.data.get("job_freshness_days_phase2", 30)

    def answer_library(self) -> dict:
        """Common recurring screening-question answers, pre-computed once."""
        d = self.data
        return {
            "years_experience": str(d.get("total_experience_years", 0)),
            "notice_period": (
                "Immediately available" if d.get("immediately_available")
                else f"{d['notice_period_days']} days"
            ),
            "current_ctc": (
                "Prefer to discuss" if d["ctc_disclosure_policy"] == "negotiable"
                else f"{d['current_ctc_lpa']} LPA"
            ),
            "expected_ctc": (
                "Negotiable" if d["ctc_disclosure_policy"] == "negotiable"
                else f"{d['expected_ctc_lpa']} LPA"
            ),
            "current_city": d["current_city"],
            "relocate": "Yes" if d.get("relocate_cities") else "No",
            "night_shift": "Yes" if d.get("night_shift_ok") else "No",
            "weekend_work": "Yes" if d.get("weekend_ok") else "No",
        }
        
        # Add resume-extracted data for AI answers
        if d.get("additional_context"):
            library["additional_context"] = d["additional_context"]
        
        if d.get("extracted_skills"):
            library["skills"] = ", ".join(d["extracted_skills"])
        
        if d.get("extracted_experience"):
            library["extracted_experience"] = str(d["extracted_experience"])
        
        if d.get("extracted_education"):
            library["education"] = d["extracted_education"]
        
        if d.get("extracted_name"):
            library["name"] = d["extracted_name"]
        
        return library
