import numpy as np  # vector operations


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    # Cosine similarity = dot(a,b) / (||a|| * ||b||)
    if a.size == 0 or b.size == 0:
        return 0.0
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1e-9  # avoid divide-by-zero
    return float(np.dot(a, b) / denom)


def score_match(resume_vec, jd_vec, present_skills: list[str], jd_skills: list[str]) -> dict:
    """Phase 3 TODO: blend embedding sim + skill overlap + title match."""
    embedding_sim = cosine_sim(resume_vec, jd_vec)  # semantic similarity
    # Fraction of JD skills found in the resume (Jaccard-like coverage)
    skill_overlap = (
        len(set(present_skills) & set(jd_skills)) / max(1, len(set(jd_skills)))
        if jd_skills
        else 0.0
    )
    # Simple weighted sum (you’ll tune/add title match later)
    final = 0.6 * embedding_sim + 0.3 * skill_overlap
    # Rounded overall score + raw components for UI transparency
    return {
        "score": round(final, 4),
        "embedding_sim": embedding_sim,
        "skill_overlap": skill_overlap,
    }
