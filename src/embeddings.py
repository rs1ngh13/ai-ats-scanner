# src/embeddings.py
from __future__ import annotations
from functools import lru_cache
from typing import Iterable
import numpy as np
import re

# Lazy import so the app starts even if packages aren’t installed yet
def _lazy_import():
    from sentence_transformers import SentenceTransformer
    import torch
    return SentenceTransformer, torch


# Choose a small, fast, high-quality model (free, no API key)
_DEFAULT_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

@lru_cache(maxsize=3)
def _get_model(model_name: str = _DEFAULT_MODEL_NAME):
    SentenceTransformer, torch = _lazy_import()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return SentenceTransformer(model_name, device=device)


def _normalize_text(s: str) -> str:
    s = (s or "").strip()
    return " ".join(s.split())


def _maybe_e5(text: str, model_name: str, is_query: bool) -> str:
    """Add required prefixes if using an E5 model."""
    if "e5" in model_name.lower():
        return f'{"query" if is_query else "passage"}: {text}'
    return text


def embed_text(
    text: str,
    model_name: str = _DEFAULT_MODEL_NAME,
    is_query: bool = False,
) -> np.ndarray:
    """
    Return a single embedding vector for the input text.
    """
    text = _normalize_text(text)
    if not text:
        return np.zeros(384, dtype=np.float32)

    text = _maybe_e5(text, model_name, is_query)
    model = _get_model(model_name)
    vec = model.encode(text, normalize_embeddings=True)
    return vec.astype(np.float32)


def embed_batch(
    texts: Iterable[str],
    model_name: str = _DEFAULT_MODEL_NAME,
    is_query: bool = False,
) -> np.ndarray:
    texts = [_maybe_e5(_normalize_text(t), model_name, is_query) for t in texts]
    if not texts:
        return np.zeros((0, 384), dtype=np.float32)
    model = _get_model(model_name)
    vecs = model.encode(texts, normalize_embeddings=True)
    return vecs.astype(np.float32)


# ---------- Chunking + pooling ----------
def _split_paragraphs(text: str) -> list[str]:
    parts = re.split(r"\n\s*\n+", text.strip())
    return [p.strip() for p in parts if len(p.strip()) > 40]


def embed_and_pool(
    text: str,
    model_name: str = _DEFAULT_MODEL_NAME,
    pool: str = "mean",
    is_query: bool = False,
) -> np.ndarray:
    chunks = _split_paragraphs(text)
    if not chunks:
        return embed_text(text, model_name, is_query=is_query)

    vecs = embed_batch(chunks, model_name, is_query=is_query)
    if vecs.size == 0:
        return embed_text(text, model_name, is_query=is_query)

    if pool == "max":
        return vecs.max(axis=0)
    return vecs.mean(axis=0)
