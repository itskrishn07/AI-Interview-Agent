import json
from pathlib import Path
from backend.services.candidate_analyzer import candidate_analyzer

def test_classify_experience_level():
    assert candidate_analyzer.classify_experience_level(1, "Intern") == "junior"
    assert candidate_analyzer.classify_experience_level(5, "Software Engineer") == "intermediate"
    assert candidate_analyzer.classify_experience_level(9, "Senior Data Engineer") == "senior"

def test_analyze_candidate():
    candidates_path = Path(__file__).resolve().parent.parent / "candidates.json"
    with open(candidates_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    candidates = data.get("candidates", [])
    assert len(candidates) > 0

    # Test Sarah Johnson (Senior Data Engineer)
    sarah_raw = candidates[0]
    profile = candidate_analyzer.analyze(sarah_raw)
    assert profile.candidate_id == "CAND-001"
    assert profile.name == "Sarah Johnson"
    assert profile.experience_level == "senior"
    assert len(profile.completed_days) > 0
    assert len(profile.probe_days) > 0

    # Test Ethan Brooks (Intern)
    ethan_raw = [c for c in candidates if c["member"]["id"] == "CAND-007"][0]
    ethan_profile = candidate_analyzer.analyze(ethan_raw)
    assert ethan_profile.experience_level == "junior"
