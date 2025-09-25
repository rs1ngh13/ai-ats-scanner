from dataclasses import dataclass
from typing import Dict, List, Optional        

@dataclass
class ParsedDoc:
    # A structured representation of a parsed resume/JD
    text: str                                  # the full cleaned text
    sections: Dict[str, str]                   # named sections (skills/experience/education)
    meta: Optional[Dict] = None                # optional metadata (e.g., source, filename)

def parse_resume(path_or_bytes) -> ParsedDoc:
    """Phase 1 TODO: extract clean text + sections from PDF/DOCX."""
    # For Phase 0, return an empty shell to prove shape; real logic comes in Phase 1
    return ParsedDoc(text="", sections={}, meta={"source": "resume"})

def parse_job(text: str) -> ParsedDoc:
    """Phase 1 TODO: normalize JD text, optionally detect title & skills."""
    # For Phase 0, pass through whatever text we got with basic metadata
    return ParsedDoc(text=text or "", sections={}, meta={"source": "job"})
