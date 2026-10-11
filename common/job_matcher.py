"""
Job matching score algorithm.

This module calculates a match score between a job posting and the user's profile
based on various factors like skills, experience, location, salary, etc.
"""
from typing import Dict, List, Optional
import re


class JobMatcher:
    """Calculate job match scores."""

    def __init__(self, profile: Dict):
        """
        Initialize the job matcher with user profile.

        Args:
            profile: User profile dictionary containing skills, experience, etc.
        """
        self.profile = profile
        self.user_skills = set(skill.lower() for skill in profile.get('skills', []))
        self.user_experience = profile.get('total_experience_years', 0)
        self.user_location = profile.get('current_city', '').lower()
        self.user_expected_ctc = profile.get('expected_ctc_lpa', 0)
        self.user_current_ctc = profile.get('current_ctc_lpa', 0)

    def calculate_match_score(self, job: Dict) -> Dict:
        """
        Calculate overall match score for a job.

        Args:
            job: Job posting dictionary

        Returns:
            Dictionary with overall score and breakdown
        """
        scores = {
            'skills_match': self._calculate_skills_match(job),
            'experience_match': self._calculate_experience_match(job),
            'location_match': self._calculate_location_match(job),
            'salary_match': self._calculate_salary_match(job),
            'role_match': self._calculate_role_match(job),
        }

        # Weight the different factors
        weights = {
            'skills_match': 0.35,
            'experience_match': 0.20,
            'location_match': 0.15,
            'salary_match': 0.15,
            'role_match': 0.15,
        }

        overall_score = sum(
            scores[factor] * weights[factor]
            for factor in scores
        )

        return {
            'overall_score': round(overall_score * 100, 1),
            'breakdown': scores,
            'recommendation': self._get_recommendation(overall_score),
        }

    def _calculate_skills_match(self, job: Dict) -> float:
        """
        Calculate skills match score.

        Args:
            job: Job posting dictionary

        Returns:
            Score between 0 and 1
        """
        job_description = job.get('description', '').lower()
        job_title = job.get('title', '').lower()
        job_skills = job.get('skills', [])

        # Extract skills from job description
        all_job_text = f"{job_title} {job_description} {' '.join(job_skills).lower()}"

        matched_skills = []
        for skill in self.user_skills:
            if skill in all_job_text:
                matched_skills.append(skill)

        if not self.user_skills:
            return 0.5  # Neutral score if no skills specified

        # Calculate match ratio
        match_ratio = len(matched_skills) / len(self.user_skills)

        # Bonus for having primary skills
        if len(matched_skills) >= min(3, len(self.user_skills)):
            match_ratio = min(1.0, match_ratio + 0.1)

        return match_ratio

    def _calculate_experience_match(self, job: Dict) -> float:
        """
        Calculate experience match score.

        Args:
            job: Job posting dictionary

        Returns:
            Score between 0 and 1
        """
        job_min_exp = job.get('min_experience', 0)
        job_max_exp = job.get('max_experience', 50)

        # If user experience is within range, high score
        if job_min_exp <= self.user_experience <= job_max_exp:
            return 1.0

        # If slightly above max, still good
        if self.user_experience <= job_max_exp + 2:
            return 0.8

        # If slightly below min, might still be suitable
        if self.user_experience >= job_min_exp - 1:
            return 0.7

        # If significantly below min
        if self.user_experience < job_min_exp - 1:
            penalty = (job_min_exp - self.user_experience) / job_min_exp
            return max(0.2, 1.0 - penalty)

        # If significantly above max
        if self.user_experience > job_max_exp + 2:
            penalty = (self.user_experience - job_max_exp) / self.user_experience
            return max(0.3, 1.0 - penalty)

        return 0.5

    def _calculate_location_match(self, job: Dict) -> float:
        """
        Calculate location match score.

        Args:
            job: Job posting dictionary

        Returns:
            Score between 0 and 1
        """
        job_location = job.get('location', '').lower()
        willing_to_relocate = self.profile.get('willing_to_relocate', False)

        # Exact match
        if self.user_location and job_location and self.user_location in job_location:
            return 1.0

        # If willing to relocate, moderate score
        if willing_to_relocate:
            return 0.7

        # If location not specified, neutral
        if not job_location or not self.user_location:
            return 0.5

        # Different location and not willing to relocate
        return 0.2

    def _calculate_salary_match(self, job: Dict) -> float:
        """
        Calculate salary match score.

        Args:
            job: Job posting dictionary

        Returns:
            Score between 0 and 1
        """
        job_min_salary = job.get('min_salary_lpa', 0)
        job_max_salary = job.get('max_salary_lpa', 0)

        # If no salary info, neutral
        if not job_min_salary and not job_max_salary:
            return 0.5

        # If job salary meets or exceeds expected CTC
        if job_min_salary >= self.user_expected_ctc:
            return 1.0

        # If job salary is close to expected CTC
        if job_min_salary >= self.user_expected_ctc * 0.9:
            return 0.8

        # If job salary is below expected but above current
        if job_min_salary >= self.user_current_ctc:
            return 0.6

        # If job salary is below current CTC
        return 0.3

    def _calculate_role_match(self, job: Dict) -> float:
        """
        Calculate role/title match score.

        Args:
            job: Job posting dictionary

        Returns:
            Score between 0 and 1
        """
        job_title = job.get('title', '').lower()
        target_roles = [role.lower() for role in self.profile.get('target_roles', [])]

        if not target_roles:
            return 0.5

        # Check if job title contains any target role keywords
        for role in target_roles:
            if role in job_title:
                return 1.0

        # Check for partial matches
        for role in target_roles:
            role_words = role.split()
            matches = sum(1 for word in role_words if word in job_title)
            if matches >= len(role_words) * 0.5:
                return 0.7

        return 0.3

    def _get_recommendation(self, score: float) -> str:
        """
        Get recommendation based on match score.

        Args:
            score: Overall match score (0-1)

        Returns:
            Recommendation string
        """
        if score >= 0.8:
            return "Highly Recommended"
        elif score >= 0.6:
            return "Recommended"
        elif score >= 0.4:
            return "Consider Applying"
        else:
            return "Not Recommended"


def calculate_job_match_score(profile: Dict, job: Dict) -> Dict:
    """
    Convenience function to calculate job match score.

    Args:
        profile: User profile dictionary
        job: Job posting dictionary

    Returns:
        Match score dictionary
    """
    matcher = JobMatcher(profile)
    return matcher.calculate_match_score(job)


def rank_jobs(profile: Dict, jobs: List[Dict]) -> List[Dict]:
    """
    Rank jobs by match score.

    Args:
        profile: User profile dictionary
        jobs: List of job posting dictionaries

    Returns:
        List of jobs with match scores, sorted by score
    """
    ranked_jobs = []
    for job in jobs:
        match_result = calculate_job_match_score(profile, job)
        ranked_jobs.append({
            **job,
            'match_score': match_result['overall_score'],
            'match_breakdown': match_result['breakdown'],
            'recommendation': match_result['recommendation'],
        })

    # Sort by match score descending
    ranked_jobs.sort(key=lambda x: x['match_score'], reverse=True)

    return ranked_jobs
