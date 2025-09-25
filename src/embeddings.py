import numpy as np


def embed_text(text: str, model: object | None = None) -> np.ndarray:
    """Phase 2 TODO: return a vector for given text (sentence-transformers)."""
    # Phase 0 placeholder: return a deterministic random vector (so shapes work)
    rng = np.random.default_rng(42)  # fixed seed for repeatability
    return rng.normal(size=(384,))  # pretend-embedding with 384 dims (MiniLM-like)
