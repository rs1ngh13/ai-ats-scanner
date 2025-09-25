from dataclasses import dataclass
from typing import Optional
import pathlib

import fitz  # PyMuPDF
from docx import Document


@dataclass
class ParsedDoc:
    text: str
    sections: dict[str, str]
    meta: Optional[dict] = None


def _read_pdf(path: pathlib.Path) -> str:
    text_parts = []
    with fitz.open(path) as doc:
        for page in doc:
            text_parts.append(page.get_text("text"))
    return "\n".join(text_parts)


def _read_docx(path: pathlib.Path) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def _normalize(s: str) -> str:
    # simple normalization; we can expand later
    lines = [ln.strip() for ln in s.splitlines()]
    lines = [ln for ln in lines if ln]  # drop empties
    return "\n".join(lines)


def parse_resume(path_or_bytes) -> ParsedDoc:
    """
    Parse a resume from PDF/DOCX path.
    For Phase 1 we return normalized full text and leave sections empty.
    """
    path = pathlib.Path(path_or_bytes)
    if path.suffix.lower() == ".pdf":
        raw = _read_pdf(path)
    elif path.suffix.lower() == ".docx":
        raw = _read_docx(path)
    else:
        raise ValueError(f"Unsupported resume format: {path.suffix}")

    text = _normalize(raw)
    return ParsedDoc(text=text, sections={}, meta={"source": "resume", "filename": path.name})


def parse_job(text_or_path: str) -> ParsedDoc:
    """
    Accept either pasted JD text or a path to a .txt file.
    """
    p = pathlib.Path(text_or_path)
    if p.exists() and p.suffix.lower() == ".txt":
        text = _normalize(p.read_text(encoding="utf-8", errors="ignore"))
    else:
        text = _normalize(text_or_path)

    return ParsedDoc(text=text, sections={}, meta={"source": "job"})
