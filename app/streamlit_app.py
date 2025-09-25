# app/streamlit_app.py
"""
Streamlit UI for the AI Resume–Job Matcher (Phase 1: Parsing).
"""

from __future__ import annotations

# --- Make sure Python can import the sibling 'src' package BEFORE any src imports ---
import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# --- Third-party & stdlib imports ---
import pathlib
import tempfile
import streamlit as st

# Optional: helpful message if parsing libs are missing
_missing = []
try:
    import fitz  # PyMuPDF
except Exception:
    _missing.append("pymupdf")

try:
    from docx import Document  # python-docx
except Exception:
    _missing.append("python-docx")

# --- Local imports (now safe because ROOT is on sys.path) ---
from src.parsing import parse_resume, parse_job  # noqa: E402


# ----------------------------- UI --------------------------------------------
st.set_page_config(page_title="AI Resume–Job Matcher", page_icon="📄", layout="centered")
st.title("📄 AI Resume–Job Matcher — Phase 1: Parsing")

if _missing:
    st.warning(
        "Missing packages: **{}**. Install with:\n\n`pip install {}`".format(
            ", ".join(_missing), " ".join(_missing)
        )
    )

st.write("Upload a resume (PDF/DOCX) and paste a JD, or use the sample files.")

resume_file = st.file_uploader("Upload resume (PDF/DOCX)", type=["pdf", "docx"])
jd_text = st.text_area("Paste job description (optional if using sample JD)", height=180)

col1, col2 = st.columns(2)
with col1:
    use_sample_resume = st.checkbox("Use sample resume from data/samples", value=False)
with col2:
    use_sample_jd = st.checkbox("Use sample JD from data/samples", value=True)

run = st.button("Parse")


# -------------------------- Helpers ------------------------------------------
def _save_upload_to_temp(upload) -> pathlib.Path:
    """Save an uploaded file to a temp path and return that path."""
    suffix = ""
    if upload and "." in upload.name:
        suffix = "." + upload.name.rsplit(".", 1)[-1].lower()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(upload.read())
    tmp.flush()
    return pathlib.Path(tmp.name)


# --------------------------- Action ------------------------------------------
if run:
    try:
        # Resolve resume path
        if use_sample_resume:
            resume_path = pathlib.Path("data/samples/sample_resume.pdf")
            if not resume_path.exists():
                alt = pathlib.Path("data/samples/sample_resume.docx")
                if alt.exists():
                    resume_path = alt
                else:
                    raise FileNotFoundError(
                        "No sample resume found in data/samples "
                        "(expected sample_resume.pdf or sample_resume.docx)."
                    )
        else:
            if not resume_file:
                st.error("Please upload a resume or check 'Use sample resume'.")
                st.stop()
            resume_path = _save_upload_to_temp(resume_file)

        parsed_resume = parse_resume(resume_path)

        # Resolve JD source
        if use_sample_jd and not jd_text.strip():
            sample_jd_path = pathlib.Path("data/samples/sample_jd.txt")
            if not sample_jd_path.exists():
                raise FileNotFoundError(
                    "No sample JD found (expected data/samples/sample_jd.txt)."
                )
            parsed_jd = parse_job(str(sample_jd_path))
        else:
            parsed_jd = parse_job(jd_text)

        # Show results
        st.success("Parsed successfully!")
        st.subheader("Resume (first 40 lines)")
        st.code("\n".join(parsed_resume.text.splitlines()[:40]) or "(empty)")

        st.subheader("Job Description (first 40 lines)")
        st.code("\n".join(parsed_jd.text.splitlines()[:40]) or "(empty)")

        with st.expander("Show metadata"):
            st.json(
                {
                    "resume_meta": parsed_resume.meta,
                    "jd_meta": parsed_jd.meta,
                    "resume_chars": len(parsed_resume.text),
                    "jd_chars": len(parsed_jd.text),
                }
            )

    except Exception as e:
        st.error(f"Parsing failed: {e}")
        st.stop()
else:
    st.info("Click **Parse** after uploading a resume and pasting a JD, "
            "or enable the sample checkboxes.")
