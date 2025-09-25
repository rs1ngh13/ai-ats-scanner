from typing import Dict, List                   # type hints

def build_explanation(present: List[str], missing: List[str]) -> Dict:
    """Phase 5 TODO: human-readable rationale."""
    # Provide a small, user-friendly summary for the UI
    return {
        "strong": present[:5],                  # top present skills
        "missing": missing[:5],                 # top missing skills
        "notes": "Add details in Phase 5."      # placeholder notes
    }
