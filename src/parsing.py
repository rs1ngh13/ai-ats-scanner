from dataclasses import dataclass
from typing import Optional
import pathlib

import fitz 
from docx import Document


@dataclass
class ParsedDoc:
    text: str
    sections: dict[str, str]
    meta: Optional[dict] = None


def _read_pdf(path: pathlib.Path) -> str:
    parts = []
    with fitz.open(path) as doc:
        for page in doc:
            parts.append(page.get_text("text"))
    return "\n".join(parts)


def _read_docx(path: pathlib.Path) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def _normalize(s: str) -> str:
    lines = [ln.strip() for ln in s.splitlines()]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)


def parse_resume(path_or_bytes) -> ParsedDoc:
    p = pathlib.Path(path_or_bytes)
    if p.suffix.lower() == ".pdf":
        raw = _read_pdf(p)
    elif p.suffix.lower() == ".docx":
        raw = _read_docx(p)
    else:
        raise ValueError(f"Unsupported resume format: {p.suffix}")
    text = _normalize(raw)
    return ParsedDoc(text=text, sections={}, meta={"source": "resume", "filename": p.name})


def parse_job(text_or_path: str) -> ParsedDoc:
    """
    Accept either pasted JD text OR a path to a .txt file.
    If the input has newlines or is long, treat it as text (not a path).
    """
    s = text_or_path or ""
    looks_like_path = (
        "\n" not in s
        and "\r" not in s
        and len(s) < 260                    # avoid OS filename limits
        and s.lower().endswith(".txt")
    )

    if looks_like_path:
        p = pathlib.Path(s)
        if p.exists() and p.is_file():
            text = _normalize(p.read_text(encoding="utf-8", errors="ignore"))
            return ParsedDoc(text=text, sections={}, meta={"source": "job", "filename": p.name})

    # Fallback: treat as raw JD text
    text = _normalize(s)
    return ParsedDoc(text=text, sections={}, meta={"source": "job"})

