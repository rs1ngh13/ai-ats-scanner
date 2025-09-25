from typing import List, Dict                   # type hints

def rank_resumes_for_job(resume_scores: List[Dict]) -> List[Dict]:
    """Phase 7 TODO: sort by score desc and return."""
    # Sort candidate score dicts by the 'score' key (highest first)
    return sorted(resume_scores, key=lambda x: x.get("score", 0), reverse=True)
