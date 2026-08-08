from typing import Dict, Any, List
from pydantic import BaseModel, Field

class CandidateProfile(BaseModel):
    candidate_id: str
    name: str
    role: str
    years_experience: int
    education: str
    status: str
    experience_level: str # junior, intermediate, senior
    completed_days: List[int] = Field(default_factory=list)
    skipped_days: List[int] = Field(default_factory=list)
    failed_days: List[int] = Field(default_factory=list)
    first_try_days: List[int] = Field(default_factory=list)
    multi_attempt_days: List[int] = Field(default_factory=list)
    probe_days: List[int] = Field(default_factory=list)
    signals: Dict[str, Any] = Field(default_factory=dict)

class CandidateAnalyzer:
    """Analyzes raw candidate json data into a structured interview profile."""
    
    @staticmethod
    def classify_experience_level(years: int, role: str) -> str:
        role_lower = role.lower()
        if "intern" in role_lower or "junior" in role_lower or years <= 2:
            return "junior"
        elif "senior" in role_lower or "distinguished" in role_lower or "principal" in role_lower or years >= 8:
            return "senior"
        else:
            return "intermediate"

    def analyze(self, raw_candidate: Dict[str, Any]) -> CandidateProfile:
        member = raw_candidate.get("member", {})
        missions = raw_candidate.get("missions", [])
        signals = raw_candidate.get("signals", {})

        candidate_id = member.get("id", "UNKNOWN")
        name = member.get("name", "Candidate")
        role = member.get("jobRole", "Software Engineer")
        years_exp = member.get("yearsExperience", 0)
        education = member.get("education", "")
        status = member.get("status", "COMPLETED")

        exp_level = self.classify_experience_level(years_exp, role)

        completed_days = []
        skipped_days = []
        failed_days = []
        first_try_days = []
        multi_attempt_days = []

        for m in missions:
            day = m.get("day")
            if not day:
                continue

            if m.get("skipped", False):
                skipped_days.append(day)
            elif m.get("passed", False):
                completed_days.append(day)
                attempts = m.get("attempts", 1)
                if attempts == 1:
                    first_try_days.append(day)
                else:
                    multi_attempt_days.append(day)
            else: # passed is False
                failed_days.append(day)

        # Priority probe days: multi-attempt passes, failed days, or skipped days
        probe_days = list(set(multi_attempt_days + failed_days + skipped_days))

        return CandidateProfile(
            candidate_id=candidate_id,
            name=name,
            role=role,
            years_experience=years_exp,
            education=education,
            status=status,
            experience_level=exp_level,
            completed_days=completed_days,
            skipped_days=skipped_days,
            failed_days=failed_days,
            first_try_days=first_try_days,
            multi_attempt_days=multi_attempt_days,
            probe_days=probe_days,
            signals=signals
        )

candidate_analyzer = CandidateAnalyzer()
